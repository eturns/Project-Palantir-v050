"""Focused P2-A contract tests; no modification of legacy scoring services."""
import json
from pathlib import Path
import pytest

from src.provisional_calibration import (
    CalibrationError, EVALUATED, CONDITIONAL, NOT_EVALUATED,
    load_reference, rate_display, rate_capabilities,
)

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_FILE = ROOT / "data" / "calibration" / "provisional_six_army_v1.json"

@pytest.fixture(scope="module")
def reference():
    return load_reference(REFERENCE_FILE)


def test_reference_is_explicitly_provisional(reference):
    assert reference["display_only"] is True
    assert reference["production_approved"] is False
    assert reference["final_calibration_approved"] is False
    assert len(reference["armies"]) == 6
    assert len(reference["metrics"]) == 6


@pytest.mark.parametrize("metric", [
    "offence_density", "army_survival_density", "per_model_resilience",
    "open_ground_mobility", "stationary_shooting", "courage_reliability",
])
def test_frozen_endpoints_exact(metric, reference):
    m = reference["metrics"][metric]
    assert rate_display(metric, m["minimum"], reference).rating == 0
    assert rate_display(metric, m["maximum"], reference).rating == 1


@pytest.mark.parametrize("metric", [
    "offence_density", "army_survival_density", "per_model_resilience",
    "open_ground_mobility", "stationary_shooting", "courage_reliability",
])
def test_all_six_reference_armies_keep_original_minmax(metric, reference):
    m = reference["metrics"][metric]
    for army in reference["armies"]:
        raw = m["reference_raw_values"][army]
        observed = rate_display(metric, raw, reference)
        expected = max(0.0, min(1.0, (raw - m["minimum"]) / (m["maximum"] - m["minimum"])))
        assert observed.rating == pytest.approx(expected, abs=1e-12)
        assert observed.raw_value == raw
        assert observed.status == EVALUATED


def test_cohort_additions_do_not_refit(reference):
    raw = reference["metrics"]["offence_density"]["reference_raw_values"]["dol_guldur"]
    baseline = rate_display("offence_density", raw, reference)
    _ = rate_display("offence_density", 9000.0, reference)
    assert rate_display("offence_density", raw, reference) == baseline


def test_unqualified_and_missing_are_not_zero(reference):
    for metric, value in (("magic", 0.0), ("hero_hunting", None), ("objective", 0.7)):
        rating = rate_display(metric, value, reference)
        assert rating.status == NOT_EVALUATED and rating.rating is None
    missing = rate_display("offence_density", None, reference)
    assert missing.status == NOT_EVALUATED and missing.rating is None
    conditional = rate_display("open_ground_mobility", 6.0, reference,
                               evidence_status=CONDITIONAL)
    assert conditional.status == CONDITIONAL and conditional.rating is None
    assert conditional.raw_value == 6.0


def test_real_zero_and_clipping_are_distinct(reference):
    zero = rate_display("stationary_shooting", 0.0, reference)
    assert zero.status == EVALUATED and zero.rating == 0
    above = rate_display("stationary_shooting", 500.0, reference)
    assert above.rating == 1 and above.clipped and above.raw_value == 500.0
    below = rate_display("open_ground_mobility", 1.0, reference)
    assert below.rating == 0 and below.clipped


def test_all_capabilities_keep_missing_as_not_evaluated(reference):
    values = {"offence_density": 0.8, "magic": None}
    scores = rate_capabilities(values, reference, evidence_statuses={"courage_reliability": CONDITIONAL})
    assert scores["offence_density"].rating is not None
    assert scores["magic"].rating is None
    assert scores["courage_reliability"].status == CONDITIONAL
    assert scores["per_model_resilience"].status == NOT_EVALUATED


def test_defence_is_display_only_without_weights(reference):
    assert reference["defence_dependency"]["independent_composite_weighting_allowed"] is False
    assert not hasattr(rate_display("army_survival_density", 2.0, reference), "weight")


def test_nonfinite_values_rejected(reference):
    with pytest.raises(CalibrationError):
        rate_display("offence_density", float("nan"), reference)
    with pytest.raises(CalibrationError):
        rate_display("offence_density", float("inf"), reference)


def test_invalid_reference_endpoints_rejected(tmp_path, reference):
    mutable = json.loads(json.dumps(reference))
    mutable["metrics"]["offence_density"]["maximum"] = mutable["metrics"]["offence_density"]["minimum"]
    p = tmp_path / "invalid.json"
    p.write_text(json.dumps(mutable))
    with pytest.raises(CalibrationError):
        load_reference(p)
