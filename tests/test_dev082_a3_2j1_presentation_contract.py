"""Project Palantír — DEV-082-A3-2J-1 read-only presentation tests."""
from copy import deepcopy
from math import nan
import pytest

from offence_presentation_contract import (
    build_offence_presentation_row,
    build_offence_presentation_cohort,
)


def sample(key="army", interval=False):
    models = 5 if interval else 3
    fixed = 3
    alternatives = 2 if interval else 0
    lo = 0.6 if not interval else 0.7
    hi = 0.6 if not interval else 0.8
    q = {
        "key": key, "status": "arithmetic_and_provenance_qualified",
        "models": models, "points": 500.0,
        "neutral_reference_models": fixed,
        "weapon_alternative_models": alternatives,
        "neutral_density_lower_per_100pts": lo,
        "neutral_density_upper_per_100pts": hi,
        "neutral_density_point_per_100pts": None if interval else lo,
        "candidate_qualification": "diagnostic_only_not_production_approved",
        "candidate_raw_density": None, "production_scoring_changed": False,
        "calibration_changed": False, "promote_to_dashboard": False,
        "comparable_with_legacy_production_density": False,
    }
    c = {
        "key": key, "status": "neutral_coverage_qualified",
        "models": models, "points": 500.0,
        "neutral_reference_models": fixed,
        "different_weapon_outcome_models": alternatives,
        "potential_support_equipped_models": 2,
        "candidate_raw_density": None, "production_scoring_changed": False,
        "calibration_changed": False, "comparable_with_legacy_army_density": False,
        "support_deployment_inferred": False,
        "conditional_frequencies_inferred": False,
    }
    a = {
        "key": key, "stage": "DEV-082-A3-2I-5",
        "status": ("charged_replay_reconciled_partial_attribution" if interval
                   else "charged_replay_reconciled_full_profile_attribution"),
        "models": models, "points": 500.0,
        "neutral_matched_models": fixed,
        "neutral_mismatched_models": 0,
        "weapon_choice_unresolved_models": alternatives,
        "unexplained_profile_mismatches": 0,
        "legacy_charged_replay_matches_production": True,
        "full_difference_attribution_possible": not interval,
        "legacy_charged_replayed_density": 0.85,
        "legacy_uncharged_replayed_density_reference_only": 0.6,
        "legacy_and_neutral_numerically_equal": False,
        "known_charge_parameter_contributions_per_100pts": 0.25,
        "profile_rows_evidence": [{"entry_index": 1}], "profile_rows": 1,
        "metric_decision": "retain_separate_neutral_melee_diagnostic_do_not_replace_composite_offence",
        "promotion_authorised": False,
        "candidate_raw_density": None, "production_scoring_changed": False,
        "calibration_changed": False,
    }
    return a, q, c


def row(interval=False):
    return build_offence_presentation_row(*sample(interval=interval))


def test_neutral_point_is_separate_from_legacy():
    result = row()
    assert result["neutral_melee"]["value"] == 0.6
    assert result["legacy_reference"]["density"] == 0.85
    assert result["legacy_reference"]["neutral_comparison_delta"] is None


def test_uncharged_contract_and_units():
    n = row()["neutral_melee"]
    assert n["benchmark"] == "F4 S4 D6 A1 W1"
    assert "uncharged" in n["conditions"]
    assert "per 100 army points" in n["unit"]
    assert n["is_overall_army_offence"] is False


def test_unresolved_weapons_form_interval_not_midpoint():
    n = row(True)["neutral_melee"]
    assert n["value_type"] == "interval"
    assert n["value"] is None
    assert (n["lower"], n["upper"]) == (.7, .8)


def test_no_inferred_support_bonus():
    support = row()["conditional_capabilities"]["support"]
    assert support["equipped_models"] == 2
    assert support["combat_bonus_value"] is None
    assert support["legally_available_support_opportunities"] is None


def test_charge_is_not_added_to_neutral():
    charge = row()["conditional_capabilities"]["charge"]
    assert charge["parameter_values_compared"] == [0.0, 1.0]
    assert charge["empirical_charge_frequency"] is None
    assert charge["additive_to_neutral_bar"] is False


def test_trap_effect_remains_conditional():
    trap = row()["conditional_capabilities"]["trapping"]
    assert trap["frequency"] is None
    assert trap["combat_bonus_value"] is None


def test_shooting_hero_hunting_and_heroic_combat_excluded():
    s = row()["safeguards"]
    assert not s["shooting_double_counted"]
    assert not s["hero_hunting_double_counted"]
    assert not s["heroic_combat_assigned_to_offence"]


def test_no_web_or_production_writes():
    r = row()
    assert r["visibility"] == "internal_preview_only_not_live_dashboard"
    assert r["safeguards"]["promotion_authorised"] is False
    assert r["safeguards"]["dashboard_score"] is None
    assert r["safeguards"]["calibration_changed"] is False


def test_inputs_are_not_modified():
    sources = sample(interval=True)
    snapshot = deepcopy(sources)
    build_offence_presentation_row(*sources)
    assert sources == snapshot


def test_numerically_matching_legacy_remains_different_contract():
    a, q, c = sample()
    a["legacy_and_neutral_numerically_equal"] = True
    r = build_offence_presentation_row(a, q, c)
    assert r["legacy_reference"]["numerical_match_with_neutral"] is True
    assert r["legacy_reference"]["same_metric_as_neutral"] is False


@pytest.mark.parametrize("source_index,field,value", [
    (0, "promotion_authorised", True),
    (1, "promote_to_dashboard", True),
    (0, "production_scoring_changed", True),
    (1, "calibration_changed", True),
    (2, "candidate_raw_density", .7),
    (0, "legacy_charged_replay_matches_production", False),
    (0, "unexplained_profile_mismatches", 1),
    (0, "neutral_mismatched_models", 1),
    (0, "metric_decision", "replace_offence"),
    (1, "candidate_qualification", "production_approved"),
    (2, "support_deployment_inferred", True),
    (2, "conditional_frequencies_inferred", True),
    (0, "status", "unknown"),
    (1, "comparable_with_legacy_production_density", True),
    (2, "comparable_with_legacy_army_density", True),
])
def test_fail_closed_on_invalid_source_contract(source_index, field, value):
    s = list(sample())
    s[source_index][field] = value
    with pytest.raises(ValueError):
        build_offence_presentation_row(*s)


def test_wrong_identity_rejected():
    a, q, c = sample()
    q["key"] = "wrong"
    with pytest.raises(ValueError, match="identity"):
        build_offence_presentation_row(a, q, c)


def test_wrong_points_rejected():
    a, q, c = sample()
    c["points"] = 600.0
    with pytest.raises(ValueError):
        build_offence_presentation_row(a, q, c)


def test_wrong_population_rejected():
    a, q, c = sample()
    c["neutral_reference_models"] = 2
    with pytest.raises(ValueError):
        build_offence_presentation_row(a, q, c)


def test_inverted_interval_rejected():
    a, q, c = sample(interval=True)
    q["neutral_density_upper_per_100pts"] = .6
    with pytest.raises(ValueError):
        build_offence_presentation_row(a, q, c)


def test_interval_cannot_be_collapsed_to_point():
    a, q, c = sample(interval=True)
    q["neutral_density_point_per_100pts"] = .75
    with pytest.raises(ValueError):
        build_offence_presentation_row(a, q, c)


def test_nan_charge_rejected():
    a, q, c = sample()
    a["known_charge_parameter_contributions_per_100pts"] = nan
    with pytest.raises(ValueError):
        build_offence_presentation_row(a, q, c)


def cohort():
    samples = [sample(key=f"army{i}", interval=(i == 2)) for i in range(6)]
    arr = [dict(
        stage="DEV-082-A3-2I-5", status="six_armies_attributed",
        rows=[s[0] for s in samples], models_examined=20,
        promotion_authorised=False, candidate_raw_density=None,
        calibration_changed=False, production_scoring_changed=False,
    ), dict(
        stage="DEV-082-A3-2I-4", status="six_armies_arithmetic_audited",
        rows=[s[1] for s in samples], models_examined=20,
        candidate_raw_density=None,
        calibration_changed=False, production_scoring_changed=False,
    ), dict(
        stage="DEV-082-A3-2I-2", status="six_armies_qualified",
        rows=[s[2] for s in samples], models_examined=20,
        candidate_raw_density=None,
        calibration_changed=False, production_scoring_changed=False,
    )]
    return arr


def test_six_army_preview():
    c = cohort()
    result = build_offence_presentation_cohort(*c)
    assert result["armies"] == 6
    assert result["models"] == 20
    assert result["rendered_to_dashboard"] is False


def test_reordered_army_rejected():
    c = cohort()
    c[1]["rows"].reverse()
    with pytest.raises(ValueError, match="order"):
        build_offence_presentation_cohort(*c)


def test_missing_army_rejected():
    c = cohort()
    c[0]["rows"].pop()
    with pytest.raises(ValueError, match="six"):
        build_offence_presentation_cohort(*c)


def test_total_population_mismatch_rejected():
    c = cohort()
    c[0]["models_examined"] = 21
    with pytest.raises(ValueError, match="totals"):
        build_offence_presentation_cohort(*c)


def test_cohort_promotion_rejected():
    c = cohort()
    c[0]["promotion_authorised"] = True
    with pytest.raises(ValueError):
        build_offence_presentation_cohort(*c)
