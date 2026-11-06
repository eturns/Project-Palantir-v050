"""DEV-082-A3-2G-2 — read-only conditional weapon resolution tests."""
from copy import deepcopy
import pytest
from offence_weapon_resolution_policy import classify_weapon_audit_row, qualify_multi_weapon_cohort


def option(weapon, p):
    return {"weapon_id": weapon, "battlefield_legality": "not_verified",
            "player_choice": "not_inferred", "conditional_probabilities": {
                "uncharged_probability": p, "charged_probability": p,
                "eligible_cavalry_charge_probability": p}}


def row(p=.2, q=.2, second="WG_SPEAR"):
    a, b = option("WG_HAND_WEAPON", p), option(second, q)
    return {"profile_id": "IH_WR", "quantity": 7,
            "candidate_weapon_ids": [a["weapon_id"], b["weapon_id"]],
            "alternatives": [a, b],
            "outcome_comparison": {state: {
                "minimum": min(p, q), "maximum": max(p, q),
                "spread": abs(p-q), "outcomes_differ": abs(p-q) > 1e-12,
            } for state in a["conditional_probabilities"]},
            "selection_status": "requires_legal_option_and_tactical_policy",
            "legal_option_verified": False}


def audit(one=None):
    one = row() if one is None else one
    return {"stage": "DEV-082-A3-2G-1", "rows": [
        {"key": "iron_hills", "status": "audited", "models": 7,
         "multiple_weapon_models": 7, "profile_audits": [one],
         "legality_verified": False, "automatic_selection_made": False,
         "candidate_raw_density": None, "production_scoring_changed": False,
         "calibration_changed": False}],
        "armies_expected": 1, "multi_weapon_models": 7,
        "candidate_raw_density": None,
        "production_scoring_changed": False, "calibration_changed": False}


def test_equal_outcomes_benchmark_equivalent():
    result = classify_weapon_audit_row(row())
    assert result["policy_status"] == "benchmark_equivalent_options"
    assert all(x["benchmark_equivalent"] for x in result["state_comparisons"].values())


def test_equivalence_not_full_tactical_equivalence():
    result = classify_weapon_audit_row(row())
    assert result["support_attack_contribution"] == "not_evaluated"
    assert result["support_capability_ids"] == ["WG_SPEAR"]
    assert result["eligible_for_unconditional_army_density"] is False


def test_two_handed_difference_remains_unselected():
    result = classify_weapon_audit_row(row(.138888, .152777, "WG_TWO_HANDED_WEAPON"))
    assert result["policy_status"] == "different_conditional_outcomes"
    assert result["selected_weapon_id"] is None
    assert result["automatic_choice_made"] is False


def test_war_spear_support_not_evaluated():
    result = classify_weapon_audit_row(row(.2,.2,"WG_WAR_SPEAR"))
    assert result["support_capability_ids"] == ["WG_WAR_SPEAR"]
    assert result["support_attack_contribution"] == "not_evaluated"


def test_no_support_weapon_not_claimed_supporting():
    result = classify_weapon_audit_row(row(.2,.3,"WG_TWO_HANDED_WEAPON"))
    assert result["support_attack_contribution"] == "not_applicable_to_catalogued_options"


def test_output_never_selects_weapon():
    result = qualify_multi_weapon_cohort(audit())
    assert result["candidate_raw_density"] is None
    assert result["dashboard_score"] is None
    assert result["production_scoring_changed"] is False
    assert result["rows"][0]["profile_resolutions"][0]["selected_weapon_id"] is None


def test_model_counts_quantity_weighted():
    result = qualify_multi_weapon_cohort(audit())
    assert result["classification_model_counts"] == {"benchmark_equivalent_options": 7}
    assert result["multiple_weapon_models"] == 7
    assert result["status"] == "complete"


def test_mixed_cohort_counts():
    d = audit()
    r = row(.2, .3, "WG_TWO_HANDED_WEAPON")
    r["quantity"] = 5
    d["rows"].append({"key": "pits", "status": "audited", "models": 5,
        "multiple_weapon_models": 5, "profile_audits": [r],
        "legality_verified": False, "automatic_selection_made": False,
        "candidate_raw_density": None, "production_scoring_changed": False,
        "calibration_changed": False})
    d["armies_expected"] = 2
    d["multi_weapon_models"] = 12
    r = qualify_multi_weapon_cohort(d)
    assert r["classification_model_counts"] == {
        "benchmark_equivalent_options": 7,
        "different_conditional_outcomes": 5}


def test_blocked_army_remains_visible():
    d = audit()
    d["rows"][0] = {"key": "iron_hills", "status": "blocked", "reason": "missing"}
    r = qualify_multi_weapon_cohort(d)
    assert r["status"] == "incomplete"
    assert r["rows"][0]["reason"] == "missing"


def test_invalid_stage_rejected():
    d = audit()
    d["stage"] = "DEV-082-A3-2G-2"
    with pytest.raises(ValueError): qualify_multi_weapon_cohort(d)


@pytest.mark.parametrize("field,value", [
    ("candidate_raw_density", .3),
    ("calibration_changed", True),
    ("production_scoring_changed", True),
])
def test_scoring_tampering_rejected(field,value):
    d = audit()
    d[field] = value
    with pytest.raises(ValueError): qualify_multi_weapon_cohort(d)


def test_legal_choice_not_fabricated():
    d = row()
    d["legal_option_verified"] = True
    with pytest.raises(ValueError): classify_weapon_audit_row(d)


def test_player_choice_not_fabricated():
    d = row()
    d["alternatives"][0]["player_choice"] = "auto"
    with pytest.raises(ValueError): classify_weapon_audit_row(d)


def test_battlefield_legality_not_fabricated():
    d = row()
    d["alternatives"][0]["battlefield_legality"] = "legal"
    with pytest.raises(ValueError): classify_weapon_audit_row(d)


def test_inconsistent_spread_rejected():
    d = row()
    d["outcome_comparison"]["uncharged_probability"]["spread"] = .1
    with pytest.raises(ValueError): classify_weapon_audit_row(d)


def test_non_finite_probability_rejected():
    d = row()
    d["alternatives"][0]["conditional_probabilities"]["charged_probability"] = float("nan")
    with pytest.raises(ValueError): classify_weapon_audit_row(d)


def test_duplicated_weapon_ids_rejected():
    d = row()
    d["candidate_weapon_ids"] = ["WG_HAND_WEAPON", "WG_HAND_WEAPON"]
    with pytest.raises(ValueError): classify_weapon_audit_row(d)


def test_wrong_army_model_total_rejected():
    d = audit()
    d["rows"][0]["multiple_weapon_models"] = 8
    with pytest.raises(ValueError): qualify_multi_weapon_cohort(d)


def test_wrong_cohort_model_total_rejected():
    d = audit()
    d["multi_weapon_models"] = 8
    with pytest.raises(ValueError): qualify_multi_weapon_cohort(d)


def test_no_mutation():
    d = audit()
    previous = deepcopy(d)
    qualify_multi_weapon_cohort(d)
    assert d == previous
