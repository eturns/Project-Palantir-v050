"""DEV-082-A3-2I-3 — numeric comparison and provenance safety tests."""
from copy import deepcopy
import pytest

from offence_neutral_mechanical_comparison import (
    compare_neutral_mechanical_army, compare_six_armies,
)


def row(entry, profile, n, status, probability=None, bounds=None):
    evidence = None
    if status == "benchmark_equivalent_neutral_reference":
        evidence = {
            "all_comparison_states_equivalent": True,
            "weapon_legality": "not_verified",
            "uncharged_probability_range": [probability, probability],
            "candidate_weapon_ids": ["WG_HAND_WEAPON", "WG_SPEAR"],
            "support_capability_ids": ["WG_SPEAR"],
        }
    elif status == "different_weapon_outcomes_unresolved":
        evidence = {
            "all_comparison_states_equivalent": False,
            "weapon_legality": "not_verified",
            "uncharged_probability_range": bounds or [.2, .4],
            "candidate_weapon_ids": ["WG_HAND_WEAPON", "WG_TWO_HANDED_WEAPON"],
            "support_capability_ids": [],
        }
    return {
        "entry_index": entry, "profile_id": profile, "quantity": n,
        "qualification": status,
        "neutral_single_model_probability": probability,
        "selected_weapon_id": None, "support_placement_inferred": False,
        "weapon_option_evidence": evidence,
    }


def army(*, different=True, unknown=False, key="a"):
    rows = [
        row(1, "A", 2, "single_option_neutral_reference", .25),
        row(2, "B", 3, "benchmark_equivalent_neutral_reference", .5),
    ]
    if different:
        rows.append(row(3, "C", 2, "different_weapon_outcomes_unresolved"))
    if unknown:
        rows.append(row(4, "D", 1, "unresolved"))
    n = 5 + (2 if different else 0) + (1 if unknown else 0)
    return {
        "key": key, "status": "neutral_coverage_qualified",
        "points": 100.0, "models": n,
        "neutral_reference_models": 5,
        "new_benchmark_equivalent_models": 3,
        "different_weapon_outcome_models": 2 if different else 0,
        "other_unresolved_models": 1 if unknown else 0,
        "coverage_ratio": 5/n,
        "profile_evidence": rows,
        "candidate_raw_density": None, "baseline_army_score": None,
        "production_scoring_changed": False, "calibration_changed": False,
        "comparable_with_legacy_army_density": False,
        "support_deployment_inferred": False,
        "conditional_frequencies_inferred": False,
        "selected_weapon_id": None,
    }


def cohort():
    rows = [army(key=f"army{i}") for i in range(6)]
    return {
        "stage": "DEV-082-A3-2I-2", "status": "six_armies_qualified",
        "armies_expected": 6, "armies_qualified": 6, "rows": rows,
        "candidate_raw_density": None,
        "production_scoring_changed": False, "calibration_changed": False,
    }


def test_fixed_model_probability_sum():
    r = compare_neutral_mechanical_army(army())
    assert r["fixed_qualified_expected_defeats"] == pytest.approx(2*.25 + 3*.5)


def test_unresolved_interval_weighted_by_quantity():
    r = compare_neutral_mechanical_army(army())
    assert r["conditional_total_expected_defeats_lower"] == pytest.approx(2.4)
    assert r["conditional_total_expected_defeats_upper"] == pytest.approx(2.8)


def test_per_100_points_normalisation():
    a = army()
    a["points"] = 200
    r = compare_neutral_mechanical_army(a)
    assert r["neutral_direct_melee_density_lower_per_100pts"] == pytest.approx(1.2)
    assert r["neutral_direct_melee_density_upper_per_100pts"] == pytest.approx(1.4)


def test_interval_does_not_generate_point_for_unresolved_choice():
    r = compare_neutral_mechanical_army(army())
    assert r["neutral_direct_melee_density_point_per_100pts"] is None
    assert r["unresolved_options_selected"] is False


def test_fully_qualified_army_has_point_and_equal_bounds():
    r = compare_neutral_mechanical_army(army(different=False))
    assert r["neutral_direct_melee_density_point_per_100pts"] == pytest.approx(2.)
    assert r["neutral_direct_melee_density_lower_per_100pts"] == pytest.approx(2.)
    assert r["neutral_direct_melee_density_upper_per_100pts"] == pytest.approx(2.)


def test_unquantified_model_suppresses_interval_not_zero():
    r = compare_neutral_mechanical_army(army(unknown=True))
    assert r["status"] == "incomplete_numeric_coverage"
    assert r["neutral_direct_melee_density_lower_per_100pts"] is None
    assert r["neutral_direct_melee_density_upper_per_100pts"] is None


def test_existing_and_new_metric_noncomparable():
    r = compare_neutral_mechanical_army(army())
    assert r["comparable_with_legacy_production_density"] is False
    assert r["candidate_raw_density"] is None
    assert r["dashboard_score"] is None


def test_combat_conditions_not_added():
    r = compare_neutral_mechanical_army(army())
    assert r["support_combat_benefit_included"] is False
    assert r["charged_or_trapping_benefit_included"] is False
    assert r["deployment_frequency_inferred"] is False


def test_source_unchanged():
    original = army()
    before = deepcopy(original)
    compare_neutral_mechanical_army(original)
    assert original == before


def test_six_army_cohort():
    r = compare_six_armies(cohort())
    assert r["status"] == "six_armies_compared"
    assert r["armies_compared"] == 6
    assert r["models_examined"] == 42
    assert r["rankings_generated"] is False


def test_six_army_fails_closed_on_missing_army():
    c = cohort()
    c["rows"].pop()
    with pytest.raises(ValueError, match="six qualified"):
        compare_six_armies(c)


def test_six_army_fails_closed_on_duplicate_key():
    c = cohort()
    c["rows"][1]["key"] = "army0"
    with pytest.raises(ValueError, match="unique"):
        compare_six_armies(c)


def test_six_army_cannot_rank_unquantified_reference():
    c = cohort()
    c["rows"][0] = army(unknown=True, key="army0")
    r = compare_six_armies(c)
    assert r["status"] == "numeric_coverage_incomplete"
    assert r["rankings_generated"] is False


@pytest.mark.parametrize("field, value", [
    ("candidate_raw_density", 0.3),
    ("baseline_army_score", 0.3),
    ("production_scoring_changed", True),
    ("calibration_changed", True),
    ("comparable_with_legacy_army_density", True),
    ("support_deployment_inferred", True),
    ("conditional_frequencies_inferred", True),
    ("selected_weapon_id", "WG_SPEAR"),
])
def test_rejects_unsafe_contract(field, value):
    a = army()
    a[field] = value
    with pytest.raises(ValueError):
        compare_neutral_mechanical_army(a)


def test_equivalent_probability_cannot_conflict():
    a = army()
    a["profile_evidence"][1]["weapon_option_evidence"]["uncharged_probability_range"] = [.5, .6]
    with pytest.raises(ValueError):
        compare_neutral_mechanical_army(a)


def test_equivalent_choice_cannot_be_marked_legal():
    a = army()
    a["profile_evidence"][1]["weapon_option_evidence"]["weapon_legality"] = "verified"
    with pytest.raises(ValueError):
        compare_neutral_mechanical_army(a)


def test_inverted_unresolved_weapon_range_fails():
    a = army()
    a["profile_evidence"][2]["weapon_option_evidence"]["uncharged_probability_range"] = [.4,.2]
    with pytest.raises(ValueError, match="reversed"):
        compare_neutral_mechanical_army(a)


def test_unresolved_option_does_not_have_selected_probability():
    a = army()
    a["profile_evidence"][2]["neutral_single_model_probability"] = .2
    with pytest.raises(ValueError):
        compare_neutral_mechanical_army(a)


@pytest.mark.parametrize("value", [-.1, 1.1, float("nan"), float("inf"), None])
def test_bad_qualified_probability(value):
    a = army()
    a["profile_evidence"][0]["neutral_single_model_probability"] = value
    with pytest.raises(ValueError):
        compare_neutral_mechanical_army(a)


def test_rejects_unmatched_population():
    a = army()
    a["models"] += 1
    with pytest.raises(ValueError):
        compare_neutral_mechanical_army(a)


def test_rejects_repeated_entry_id():
    a = army()
    a["profile_evidence"][1]["entry_index"] = 1
    with pytest.raises(ValueError, match="entry"):
        compare_neutral_mechanical_army(a)


def test_rejects_row_selected_weapon():
    a = army()
    a["profile_evidence"][2]["selected_weapon_id"] = "WG_HAND_WEAPON"
    with pytest.raises(ValueError, match="Weapon selection"):
        compare_neutral_mechanical_army(a)


def test_rejects_dishonest_new_equivalent_count():
    a = army()
    a["new_benchmark_equivalent_models"] = 2
    with pytest.raises(ValueError):
        compare_neutral_mechanical_army(a)


def test_six_army_rejects_changed_calibration():
    c = cohort()
    c["calibration_changed"] = True
    with pytest.raises(ValueError):
        compare_six_armies(c)
