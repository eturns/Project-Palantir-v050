"""B8-B2: conservative contract and six-army coverage tests."""
import pytest
from i2i_c3_b8b2_mechanical_coverage import build_report, MEASUREMENT_STATE
from unified_capability_inventory import METRIC_NAMES


@pytest.fixture(scope="module")
def report():
    return build_report()


def test_six_armies(report):
    assert len(report["armies"]) == 6


def test_canonical_ten_metrics_in_every_army(report):
    for army in report["armies"]:
        assert tuple(x["metric"] for x in army["metric_coverage"]) == METRIC_NAMES


def test_only_five_available_measurement_interfaces():
    assert sum(state == "available" for state in MEASUREMENT_STATE.values()) == 5


def test_magic_partial_and_context_dependent_metrics():
    assert MEASUREMENT_STATE["magic"] == "partial"
    for metric in ("control", "command", "objective", "hero_hunting"):
        assert MEASUREMENT_STATE[metric] == "context_required"


def test_no_invented_values(report):
    assert all(metric["value"] is None for army in report["armies"]
               for metric in army["metric_coverage"])


def test_not_calibration_approved(report):
    assert report["calibration_anchors_approved"] is False
    assert report["full_special_rules_approved"] is False
    assert report["archetype_review_approved"] is False
    assert report["production_scoring_modified"] is False


def test_equipment_failures_block_all_individual_army_metrics():
    input_report = {"results": [{
        "army":"example", "status":"blocked", "resolved_shooters":0
    }]}
    report = build_report(input_report)
    assert all(x["measurement_status"] == "blocked_by_equipment"
               for x in report["armies"][0]["metric_coverage"])


def test_zero_ranged_models_not_a_fake_zero_score(report):
    dol = next(army for army in report["armies"] if army["army"] == "dol_guldur")
    assert dol["known_resolved_ranged_models"] == 0
    assert next(x for x in dol["metric_coverage"]
                if x["metric"] == "shooting")["value"] is None
