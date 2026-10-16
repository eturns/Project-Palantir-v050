"""DEV-077S-I2-I-P2-C3-E: live six-army calibration and isolation gate.

Read-only regression: loads actual configured six-army reference fixtures.
Compare current mechanics to the immutable v2 historical measurements.
Any mismatch should fail loudly; never modify anchors to make a failure pass.
Run from the repository root with Python 3.14.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from i2i_c3_b8a_cohort_intake import FIXTURES
from i2i_c3_b8b_mechanical_qualification import load_reference_army_with_platforms
from defence_presentation_contract import build_defence_presentation
from provisional_calibration import load_reference, rate_display
from provisional_desktop_view import build_provisional_desktop_view
from provisional_mechanical_measurements import collect_provisional_mechanical_evidence


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_FILE = ROOT / "data" / "calibration" / "provisional_six_army_v2.json"
REFERENCE = load_reference(REFERENCE_FILE)

MECHANICAL_KEYS = (
    "offence_density",
    "stationary_shooting",
    "open_ground_mobility",
    "courage_reliability",
)
DEFENCE_KEYS = ("army_survival_density", "per_model_resilience")
ALL_KEYS = MECHANICAL_KEYS + DEFENCE_KEYS

# These are historical snapshots, not independently validated population anchors.
# Tight tolerance catches drift while allowing ordinary floating-point rounding.
REL_TOL = 1e-8
ABS_TOL = 1e-9


@pytest.fixture(scope="module", params=tuple(FIXTURES))
def reference_army(request):
    key = request.param
    path = ROOT / "tests" / "fixtures" / FIXTURES[key][0]
    assert path.is_file(), f"Reference fixture missing: {path}"
    army = load_reference_army_with_platforms(path)
    return key, army


def _readings(army):
    mechanical = collect_provisional_mechanical_evidence(army)
    defence = build_defence_presentation(army)
    values = dict(mechanical.values)
    statuses = dict(mechanical.statuses)
    values["army_survival_density"] = defence.army_survival_density.value
    values["per_model_resilience"] = defence.per_model_resilience.value
    statuses.update({key: "evaluated" for key in DEFENCE_KEYS})
    return values, statuses


def test_live_reference_army_matches_six_historical_raw_measurements(reference_army):
    key, army = reference_army
    values, statuses = _readings(army)
    for metric in ALL_KEYS:
        assert statuses.get(metric) == "evaluated", (
            f"{key}/{metric}: evidence not evaluated, not a valid zero"
        )
        assert metric in values, f"{key}/{metric}: measurement missing"
        expected = REFERENCE["metrics"][metric]["reference_raw_values"][key]
        assert values[metric] == pytest.approx(
            expected, rel=REL_TOL, abs=ABS_TOL
        ), f"{key}/{metric}: mechanical drift against frozen v2 reference"


def test_live_reference_army_matches_frozen_provisional_bars(reference_army):
    key, army = reference_army
    values, statuses = _readings(army)
    for metric in ALL_KEYS:
        expected_raw = REFERENCE["metrics"][metric]["reference_raw_values"][key]
        expected_rating = expected_raw / REFERENCE["metrics"][metric]["maximum"]
        got = rate_display(metric, values[metric], REFERENCE,
                           evidence_status=statuses[metric])
        assert got.status == "evaluated"
        assert got.rating == pytest.approx(
            expected_rating, rel=REL_TOL, abs=ABS_TOL
        ), f"{key}/{metric}: display rating drift"
        assert got.raw_value == pytest.approx(values[metric])
        assert got.clipped is False


def test_real_desktop_view_has_no_independent_defence_double_weighting(reference_army):
    _, army = reference_army
    mechanical = collect_provisional_mechanical_evidence(army)
    defence = build_defence_presentation(army)
    dto = {
        "army_survival_density": {
            "value": defence.army_survival_density.value, "calibrated": False
        },
        "per_model_resilience": {
            "value": defence.per_model_resilience.value, "calibrated": False
        },
    }
    view = build_provisional_desktop_view(
        dto,
        qualified_measurements=mechanical.values,
        evidence_statuses=mechanical.statuses,
    )
    assert view["display_only"] is True
    assert view["production_scoring_changed"] is False
    assert view["defence_independent_composite_weighting_allowed"] is False
    rows = {row["metric_id"]: row for row in view["metrics"]}
    for metric in ALL_KEYS:
        assert rows[metric]["status"] == "evaluated"
        assert rows[metric]["rating"] is not None
    for metric in ("magic", "hero_hunting", "control", "command", "objective"):
        assert rows[metric]["rating"] is None
        assert rows[metric]["status"] in ("not_evaluated", "conditional")


def test_display_does_not_mutate_army_or_mechanical_evidence(reference_army):
    _, army = reference_army
    mechanical = collect_provisional_mechanical_evidence(army)
    prior_values = deepcopy(mechanical.values)
    prior_statuses = deepcopy(mechanical.statuses)
    old_points = army.total_points()
    old_models = army.model_count()
    view = build_provisional_desktop_view(
        None, qualified_measurements=mechanical.values,
        evidence_statuses=mechanical.statuses,
    )
    assert view["production_scoring_changed"] is False
    assert mechanical.values == prior_values
    assert mechanical.statuses == prior_statuses
    assert army.total_points() == old_points
    assert army.model_count() == old_models


def test_reference_version_and_maxima_are_fixed():
    assert REFERENCE["display_only"] is True
    assert REFERENCE["production_approved"] is False
    assert set(REFERENCE["armies"]) == set(FIXTURES)
    for metric in ALL_KEYS:
        values = REFERENCE["metrics"][metric]["reference_raw_values"]
        assert set(values) == set(FIXTURES)
        assert REFERENCE["metrics"][metric]["maximum"] == pytest.approx(max(values.values()))
        assert REFERENCE["metrics"][metric]["mapping_method"] == "zero_to_frozen_maximum"


def test_legacy_scenario_results_not_modified_by_desktop_adapter(monkeypatch):
    """A boundary check, not an independently stored scenario-score baseline."""
    import desktop_analysis_adapter as adapter

    sentinel = {
        "army": object(),
        "scenario_analysis_results": [
            {"scenario_id": "HOLD_GROUND", "score": 0.731}
        ],
        "analysis": {
            "metric_assessments": ("legacy",),
            "validation_errors": (),
        },
    }
    before = deepcopy(sentinel["scenario_analysis_results"])
    view = {"defence_presentation": None, "scenarios": ("unchanged",)}
    monkeypatch.setattr(adapter, "run_analysis_workflow",
                        lambda path, print_report=False: sentinel)
    monkeypatch.setattr(adapter, "build_desktop_analysis_view_model",
                        lambda result: view)
    result = adapter.run_analysis("dummy.json")
    assert sentinel["scenario_analysis_results"] == before
    assert result["scenarios"] == ("unchanged",)
    assert result["provisional_capabilities"]["production_scoring_changed"] is False


def test_provisional_calibration_does_not_import_optimiser_or_scenario_services():
    """Dependency-level isolation; behavioural optimiser golden checks remain separate."""
    import inspect
    import provisional_calibration
    source = inspect.getsource(provisional_calibration)
    for forbidden in ("from optimiser", "import optimiser",
                      "from scenario_", "import scenario_"):
        assert forbidden not in source
