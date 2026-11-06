"""DEV-082-A3-2I-1: no guessed weights, allocation or production score."""
from copy import deepcopy
from math import isclose
from types import SimpleNamespace as S
import pytest

from offence_aggregation_methodology import (
    METHOD, classify_army_methodology, build_methodology_cohort,
)
from offence_explicit_army_aggregation import make_fielded_offence_roster


def army():
    entries = [
        S(counts_as_model=True, quantity=2,
          configured_profile=S(profile=S(id="F"), effective_wargear=[S(id="WG_HAND_WEAPON")])),
        S(counts_as_model=True, quantity=3,
          configured_profile=S(profile=S(id="F"), effective_wargear=[S(id="WG_SPEAR")])),
        S(counts_as_model=True, quantity=1,
          configured_profile=S(profile=S(id="X"), effective_wargear=[S(id="WG_HAND_WEAPON")])),
    ]
    return S(entries=entries, model_count=lambda: 6)


def evidence():
    return {
        "stage": "DEV-082-A3-2E", "fielded_models": 6,
        "army_points": 700, "legacy_raw_density": .8,
        "production_scoring_changed": False, "calibration_changed": False,
        "candidate_raw_density": None, "comparable": False,
        "trapping_frequency_assumed": False,
        "profile_rows": [
            {"profile_id": "F", "quantity": 2,
             "weapon_options": {"status": "single_recognised_option"},
             "trapping_benchmark_status": "paired_conditional_outcomes",
             "trapping_benchmark": {"conditional_combat_states": [
                 {"state": "uncharged", "untrapped_probability": .25},
                 {"state": "charged", "untrapped_probability": .5},
                 {"state": "eligible_cavalry_charge", "untrapped_probability": .75},
             ]}},
            {"profile_id": "F", "quantity": 3,
             "weapon_options": {"status": "multiple_options"},
             "trapping_benchmark_status": "weapon_unresolved_no_trapping_comparison",
             "trapping_benchmark": None},
            {"profile_id": "X", "quantity": 1,
             "weapon_options": {"status": "unresolved"},
             "trapping_benchmark_status": "weapon_unresolved_no_trapping_comparison",
             "trapping_benchmark": None},
        ],
    }


def result():
    return classify_army_methodology("example", evidence(), make_fielded_offence_roster(army()))


def test_reconcile_all_models():
    r = result()
    assert r["neutral_baseline_reference_models"] == 2
    assert r["multiple_weapon_models_unselected"] == 3
    assert r["other_unresolved_models"] == 1
    assert r["models"] == 6


def test_support_wargear_is_not_active_support():
    r = result()
    assert r["potential_support_equipped_models"] == 3
    assert r["baseline_army_score"] is None


def test_existing_legacy_density_not_neutral_candidate():
    r = result()
    assert r["legacy_raw_density_production_reference_only"] == .8
    assert r["candidate_raw_density"] is None
    assert r["legacy_and_neutral_scores_comparable"] is False


def test_uncertainty_kept_explicit():
    r = result()
    assert r["conditional_weights"] is None
    assert "charge_and_trap_frequency_unknown" in r["score_blockers"]


def test_unselected_multi_option_has_no_probability():
    r = result()
    assert r["profile_evidence"][1]["neutral_single_model_probability"] is None
    assert r["profile_evidence"][1]["selected_weapon_id"] is None


def test_single_option_probability_retained_only_for_reference():
    r = result()
    assert r["profile_evidence"][0]["neutral_single_model_probability"] == .25
    assert r["neutral_baseline_coverage_ratio"] == pytest.approx(1/3)


def test_different_same_profile_rows_preserve_order():
    r = result()
    assert [x["entry_index"] for x in r["profile_evidence"]] == [1, 2, 3]


def test_read_only_input():
    e, roster = evidence(), make_fielded_offence_roster(army())
    a, b = deepcopy(e), deepcopy(roster)
    classify_army_methodology("x", e, roster)
    assert e == a and roster == b


@pytest.mark.parametrize("field, val", [
    ("stage", "DEV-082-A3-2D"),
    ("production_scoring_changed", True),
    ("calibration_changed", True),
    ("candidate_raw_density", .3),
    ("comparable", True),
    ("trapping_frequency_assumed", True),
])
def test_fail_closed_source_contract(field, val):
    e = evidence(); e[field] = val
    with pytest.raises(ValueError):
        classify_army_methodology("x", e, make_fielded_offence_roster(army()))


def test_missing_uncharged_state_fails():
    e = evidence()
    e["profile_rows"][0]["trapping_benchmark"]["conditional_combat_states"][0]["state"] = "other"
    with pytest.raises(ValueError):
        classify_army_methodology("x", e, make_fielded_offence_roster(army()))


def test_probability_above_one_fails():
    e = evidence()
    e["profile_rows"][0]["trapping_benchmark"]["conditional_combat_states"][0]["untrapped_probability"] = 1.01
    with pytest.raises(ValueError):
        classify_army_methodology("x", e, make_fielded_offence_roster(army()))


def test_count_mismatch_fails():
    e = evidence(); e["fielded_models"] = 7
    with pytest.raises(ValueError):
        classify_army_methodology("x", e, make_fielded_offence_roster(army()))


def test_misordered_same_profile_entries_fail_not_silently_misassigned():
    e = evidence()
    e["profile_rows"][0]["quantity"] = 3
    e["profile_rows"][1]["quantity"] = 2
    with pytest.raises(ValueError):
        classify_army_methodology("x", e, make_fielded_offence_roster(army()))


def test_six_army_mock_cohort():
    c = build_methodology_cohort(
        fixtures=[(f"a{i}", str(i)) for i in range(6)],
        loader=lambda _: army(), reporter=lambda _: evidence(),
        roster_builder=make_fielded_offence_roster,
    )
    assert c["status"] == "six_armies_qualified"
    assert c["models_examined"] == 36
    assert c["neutral_reference_models"] == 12
    assert c["weapon_choice_unresolved_models"] == 18
    assert c["candidate_raw_density"] is None


def test_incomplete_cohort_visible():
    def load(f):
        if f == "bad": raise ValueError("fixture missing")
        return army()
    c = build_methodology_cohort(
        fixtures=[("ok", "ok"), ("bad", "bad")],
        loader=load, reporter=lambda _: evidence(),
        roster_builder=make_fielded_offence_roster,
    )
    assert c["status"] == "incomplete" and c["armies_qualified"] == 1
    assert c["rows"][1]["status"] == "blocked"


def test_methodology_excludes_other_capabilities_from_offence():
    assert set(METHOD["no_double_count"]) == {
        "shooting_excluded", "hero_hunting_excluded",
        "heroic_combat_excluded", "supporter_not_independent_fighter",
    }


def test_no_scenario_or_dashboard_changes():
    c = build_methodology_cohort(
        fixtures=[("x", "x")], loader=lambda _: army(),
        reporter=lambda _: evidence(), roster_builder=make_fielded_offence_roster,
    )
    assert c["dashboard_score"] is None
    assert c["scenario_score"] is None
    assert c["calibration_changed"] is False
    assert c["production_scoring_changed"] is False
