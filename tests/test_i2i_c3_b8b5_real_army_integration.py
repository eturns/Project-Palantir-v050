"""B8-B5 final focused integration checks."""
import pytest
from i2i_c3_b8b5_real_army_integration import build_report

@pytest.fixture(scope="module")
def report():
    return build_report()

def test_six_real_armies_import(report):
    assert report["armies_imported"] == 6, report["import_errors"]
    assert not report["import_errors"]

def test_no_runtime_check_blocked(report):
    failures = [x for x in report["checks"] if x["status"] == "blocked"]
    assert not failures, failures

def test_savage_hunters_runtime_contrasts(report):
    checks={x["check"]:x for x in report["checks"]}
    for key in ("azogs_hunters", "pits_of_dol_guldur"):
        row = checks[f"{key}:savage_hunters"]
        assert row["status"] == "verified"
        assert row["charged"] == row["charged_without_rule"] + 1
        assert row["was_charged"] == row["was_charged_without_rule"]

def test_bard_exchange_and_crossbow_runtime(report):
    checks={x["check"]:x for x in report["checks"]}
    assert checks["five_armies:bard_bow_exchange"]["status"]=="verified"
    assert checks["five_armies:six_crossbows"]["status"]=="verified"

def test_deadly_shot_runtime(report):
    checks={x["check"]:x for x in report["checks"]}
    assert checks["mirkwood:deadly_shot_attack_count"]["status"]=="verified"

def test_harbinger_distance_contrast(report):
    checks={x["check"]:x for x in report["checks"]}
    assert checks["dol_guldur:harbinger_range"]["status"]=="verified"

def test_non_approval_guardrails(report):
    for name in ("full_profile_mechanics_approved","archetype_review_approved",
                 "calibration_anchors_approved","production_scoring_modified"):
        assert report[name] is False

def test_conditional_platform_remains_not_approved(report):
    checks={x["check"]:x for x in report["checks"]}
    assert checks["iron_hills:chariot"]["status"]=="conditional"
