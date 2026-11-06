"""DEV-082-A3-2I-2 neutral completeness and option-equivalence acceptance."""
from copy import deepcopy
import pytest

from offence_neutral_baseline_completeness import (
    qualify_neutral_baseline_completeness, build_neutral_baseline_cohort,
)


def method():
    return {
        "key": "example", "status": "methodology_qualified",
        "points": 700.0, "models": 8,
        "neutral_baseline_reference_models": 2,
        "multiple_weapon_models_unselected": 6,
        "potential_support_equipped_models": 6,
        "profile_evidence": [
            {"entry_index": 1, "profile_id": "SINGLE", "quantity": 2,
             "qualification": "reference_available_not_final_score",
             "neutral_single_model_probability": .23,
             "selected_weapon_id": None, "support_placement_inferred": False},
            {"entry_index": 2, "profile_id": "IH_WR", "quantity": 3,
             "qualification": "option_choice_not_assumed",
             "neutral_single_model_probability": None,
             "selected_weapon_id": None, "support_placement_inferred": False},
            {"entry_index": 3, "profile_id": "DG_HOW", "quantity": 2,
             "qualification": "option_choice_not_assumed",
             "neutral_single_model_probability": None,
             "selected_weapon_id": None, "support_placement_inferred": False},
            {"entry_index": 4, "profile_id": "IH_WR", "quantity": 1,
             "qualification": "option_choice_not_assumed",
             "neutral_single_model_probability": None,
             "selected_weapon_id": None, "support_placement_inferred": False},
        ],
        "baseline_army_score": None, "candidate_raw_density": None,
        "calibration_changed": False, "production_scoring_changed": False,
        "legacy_and_neutral_scores_comparable": False,
        "conditional_weights": None,
    }


def option(profile, n, *, different=False):
    states = {}
    for s in ("uncharged", "charged", "eligible_cavalry_charge"):
        low = .16
        high = .17 if different else low
        states[s] = {
            "minimum_probability": low, "maximum_probability": high,
            "difference": high-low, "benchmark_equivalent": not different,
        }
    return {
        "profile_id": profile, "quantity": n,
        "policy_status": ("different_conditional_outcomes" if different
                          else "benchmark_equivalent_options"),
        "state_comparisons": states,
        "candidate_weapon_ids": ["WG_HAND_WEAPON", "WG_SPEAR"],
        "support_capability_ids": ["WG_SPEAR"],
        "benchmark_equivalence_scope": "ordinary_single_wound_direct_melee_only",
        "weapon_legality": "not_verified",
        "selected_weapon_id": None, "automatic_choice_made": False,
        "eligible_for_unconditional_army_density": False,
    }


def weapons():
    return {
        "key": "example", "status": "qualified", "models": 8,
        "multiple_weapon_models": 6,
        "status_model_counts": {
            "benchmark_equivalent_options": 4,
            "different_conditional_outcomes": 2,
        },
        "profile_resolutions": [
            option("IH_WR", 3),
            option("DG_HOW", 2, different=True),
            option("IH_WR", 1),
        ],
    }


def qualify(a=None, b=None):
    return qualify_neutral_baseline_completeness(
        method() if a is None else a,
        weapons() if b is None else b,
    )


def test_qualified_population_2_plus_4_plus_2():
    r=qualify()
    assert r["models"] == 8
    assert r["neutral_reference_models"] == 6
    assert r["new_benchmark_equivalent_models"] == 4
    assert r["different_weapon_outcome_models"] == 2
    assert r["coverage_ratio"] == .75


def test_duplicate_profile_ids_different_configurations_kept_distinct():
    r=qualify()
    rows=[x for x in r["profile_evidence"] if x["profile_id"] == "IH_WR"]
    assert len(rows) == 2
    assert [x["entry_index"] for x in rows] == [2,4]


def test_equivalent_neutral_value_copied_without_weapon_selection():
    r=qualify()
    assert r["profile_evidence"][1]["neutral_single_model_probability"] == pytest.approx(.16)
    assert r["profile_evidence"][1]["selected_weapon_id"] is None


def test_different_weapon_outcomes_remain_unresolved():
    row=qualify()["profile_evidence"][2]
    assert row["neutral_single_model_probability"] is None
    assert row["qualification"] == "different_weapon_outcomes_unresolved"
    assert row["weapon_option_evidence"]["uncharged_probability_range"] == pytest.approx([.16,.17])


def test_equivalent_direct_melee_does_not_discard_spear_utility():
    row=qualify()["profile_evidence"][1]
    assert row["weapon_option_evidence"]["support_capability_ids"] == ["WG_SPEAR"]
    assert row["weapon_option_evidence"]["weapon_legality"] == "not_verified"


def test_existing_single_reference_is_unchanged():
    row=qualify()["profile_evidence"][0]
    assert row["neutral_single_model_probability"] == .23
    assert row["qualification"] == "single_option_neutral_reference"


def test_no_army_score_and_frozen_contract():
    r=qualify()
    assert r["baseline_army_score"] is None
    assert r["candidate_raw_density"] is None
    assert r["comparable_with_legacy_army_density"] is False
    assert r["production_scoring_changed"] is False
    assert r["calibration_changed"] is False


def test_never_inferring_support_placement_or_conditional_frequencies():
    r=qualify()
    assert r["support_deployment_inferred"] is False
    assert r["conditional_frequencies_inferred"] is False
    assert all(x["support_placement_inferred"] is False for x in r["profile_evidence"])


def test_source_immutable():
    a,b=method(),weapons()
    aa,bb=deepcopy(a),deepcopy(b)
    qualify(a,b)
    assert a == aa and b == bb


@pytest.mark.parametrize("attribute, value", [
    ("candidate_raw_density", .7),
    ("calibration_changed", True),
    ("production_scoring_changed", True),
    ("baseline_army_score", .7),
    ("legacy_and_neutral_scores_comparable", True),
    ("conditional_weights", {"trapping": .5}),
])
def test_rejects_modified_methodology_scoring_contract(attribute,value):
    a=method()
    a[attribute]=value
    with pytest.raises(ValueError):
        qualify(a=a)


def test_army_identity_must_match():
    b=weapons()
    b["key"]="other"
    with pytest.raises(ValueError,match="identities"):
        qualify(b=b)


def test_model_count_must_match():
    b=weapons()
    b["models"]=9
    with pytest.raises(ValueError,match="model counts"):
        qualify(b=b)


def test_fails_if_option_row_is_missing():
    b=weapons()
    b["profile_resolutions"].pop()
    with pytest.raises(ValueError):
        qualify(b=b)


def test_rejects_option_row_order_mismatch_even_same_profile():
    b=weapons()
    b["profile_resolutions"][0],b["profile_resolutions"][1] = (
        b["profile_resolutions"][1],b["profile_resolutions"][0])
    with pytest.raises(ValueError,match="order"):
        qualify(b=b)


def test_rejects_option_row_quantity_mismatch():
    b=weapons()
    b["profile_resolutions"][0]["quantity"]=2
    with pytest.raises(ValueError):
        qualify(b=b)


def test_rejects_fabricated_equivalence():
    b=weapons()
    b["profile_resolutions"][0]["state_comparisons"]["charged"]["maximum_probability"]=.2
    with pytest.raises(ValueError):
        qualify(b=b)


def test_rejects_incomplete_state_coverage():
    b=weapons()
    del b["profile_resolutions"][0]["state_comparisons"]["charged"]
    with pytest.raises(ValueError,match="states"):
        qualify(b=b)


def test_rejects_weapon_selection():
    b=weapons()
    b["profile_resolutions"][0]["selected_weapon_id"]="WG_SPEAR"
    with pytest.raises(ValueError,match="choice"):
        qualify(b=b)


def test_rejects_weapon_legality_claim():
    b=weapons()
    b["profile_resolutions"][0]["weapon_legality"]="verified"
    with pytest.raises(ValueError,match="legality"):
        qualify(b=b)


def test_rejects_unverified_single_option_probability():
    a=method()
    a["profile_evidence"][0]["neutral_single_model_probability"]=None
    with pytest.raises(ValueError):
        qualify(a=a)


def test_rejects_mismatched_class_totals():
    b=weapons()
    b["status_model_counts"]["benchmark_equivalent_options"]=3
    with pytest.raises(ValueError):
        qualify(b=b)


def test_six_army_mock_cohort_and_totals():
    result=build_neutral_baseline_cohort(
        fixtures=[("example",str(i)) for i in range(6)],
        loader=lambda path: path,
        methodology_reporter=lambda army,key: method(),
        weapon_reporter=lambda army,key: weapons(),
    )
    assert result["status"] == "six_armies_qualified"
    assert result["models_examined"] == 48
    assert result["neutral_reference_models"] == 36
    assert result["different_weapon_outcome_models"] == 12


def test_blocked_army_is_visible_and_not_complete():
    def load(path):
        if path == "broken":
            raise RuntimeError("missing fixture")
        return path
    result=build_neutral_baseline_cohort(
        fixtures=[("example","working"),("example","broken")],
        loader=load,
        methodology_reporter=lambda army,key: method(),
        weapon_reporter=lambda army,key: weapons(),
    )
    assert result["status"] == "incomplete"
    assert result["rows"][1]["status"] == "blocked"
    assert result["armies_qualified"] == 1


def test_no_silent_autoselection_even_if_all_uncharged_equal():
    b=weapons()
    differing=b["profile_resolutions"][1]
    differing["state_comparisons"]["uncharged"]={
        "minimum_probability": .16, "maximum_probability": .16,
        "difference": 0., "benchmark_equivalent": True,
    }
    r=qualify(b=b)
    assert r["different_weapon_outcome_models"] == 2
    assert r["neutral_reference_models"] == 6
