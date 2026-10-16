"""B8-B3 tests: robust, non-approving rule inventory."""
from types import SimpleNamespace as S
import pytest
from i2i_c3_b8b3_profile_rule_audit import roster_rule_exposure, build_report


def assignment(rid, parameter=None):
    return S(rule=S(id=rid), parameter=parameter)


def test_rule_exposure_counts_models_and_parameters():
    m1 = S(configured_profile=S(profile=S(id="A"),
                               effective_special_rules=[assignment("TERROR"),
                                                        assignment("HATRED", "ELF")]))
    m2 = S(configured_profile=S(profile=S(id="B"),
                               effective_special_rules=[assignment("TERROR")]))
    army = S(fielded_models=lambda: [m1, m2, S(configured_profile=None)])
    count, rules = roster_rule_exposure(army)
    assert count == 2
    terror = next(r for r in rules if r["rule_id"] == "TERROR")
    hatred = next(r for r in rules if r["rule_id"] == "HATRED")
    assert terror["affected_models"] == 2
    assert hatred["parameters"] == ["ELF"]
    assert all(r["mechanical_verification"] == "not_evaluated" for r in rules)


def test_duplicate_rule_assignment_not_double_counted():
    model = S(configured_profile=S(profile=S(id="X"),
        effective_special_rules=[assignment("FLY"), assignment("FLY")]))
    _, rules = roster_rule_exposure(S(fielded_models=lambda: [model]))
    assert rules[0]["affected_models"] == 1


def test_equipment_block_does_not_import():
    result = build_report(importer=lambda p: (_ for _ in ()).throw(RuntimeError("called")),
                          equipment_report={"results": [{"army": k, "status": "blocked"}
                          for k in ("dol_guldur", "azogs_hunters", "pits_of_dol_guldur",
                                    "rangers_of_mirkwood", "five_armies", "iron_hills")]})
    assert result["armies_inventoried"] == 0
    assert all(x["status"] == "blocked" for x in result["armies"])


@pytest.fixture(scope="module")
def report():
    return build_report()


def test_six_armies_inventoried(report):
    assert report["candidates"] == 6
    assert report["armies_inventoried"] == 6, [
        (r["army"], r["issues"]) for r in report["armies"] if r["issues"]]


def test_every_army_has_real_model_count(report):
    assert all(isinstance(r["models_scanned"], int) and r["models_scanned"] > 0
               for r in report["armies"])


def test_no_unreviewed_rules_are_auto_approved(report):
    assert all(r["special_rules_approved"] is False for r in report["armies"])
    assert all(rule["mechanical_verification"] == "not_evaluated"
               for army in report["armies"] for rule in army["rules"])
    assert report["full_special_rules_approved"] is False
    assert report["calibration_anchors_approved"] is False
    assert report["production_scoring_modified"] is False
