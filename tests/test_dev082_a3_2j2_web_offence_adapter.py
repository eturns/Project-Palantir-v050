"""DEV-082-A3-2J-2 opt-in web mapper and diagnostic serializer tests.
Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).
"""
import json
from copy import deepcopy

import pytest
from web.backend.offence_diagnostic_adapter import build_provisional_offence_api_evidence
from web.backend.result_mapper import build_web_analysis_result


def row(*, alternatives=0):
    low, high = (1.09, 1.10) if alternatives else (.69, .69)
    return {
        "stage": "DEV-082-A3-2J-1", "status": "diagnostic_presentation_contract_qualified",
        "visibility": "internal_preview_only_not_live_dashboard", "army_key": "test_army",
        "neutral_melee": {
            "unit": "conditional expected single-wound defeats per 100 army points",
            "benchmark": "F4 S4 D6 A1 W1",
            "conditions": "one independent combat per model; uncharged; untrapped",
            "value_type": "interval" if alternatives else "point",
            "value": None if alternatives else low,
            "lower": low, "upper": high,
            "qualifying_models": 5, "unresolved_weapon_alternative_models": alternatives,
            "is_overall_army_offence": False, "is_battlefield_forecast": False,
        },
        "conditional_capabilities": {
            "charge": {"evidence": "legacy_parameter_replay_only",
                       "parameter_values_compared": [0.0, 1.0],
                       "known_qualified_profile_contribution_per_100pts": .08,
                       "full_profile_attribution": alternatives == 0,
                       "empirical_charge_frequency": None,
                       "additive_to_neutral_bar": False},
            "support": {"equipped_models": 2,
                        "legally_available_support_opportunities": None,
                        "combat_bonus_value": None, "additive_to_neutral_bar": False},
            "trapping": {"frequency": None, "combat_bonus_value": None,
                         "additive_to_neutral_bar": False},
            "weapon_alternatives": {"affected_models": alternatives,
                                    "legal_selection_confirmed": False,
                                    "optimal_weapon_selected": False},
        },
        "legacy_reference": {"density": .75, "uncharged_replay_density": .69,
                             "same_metric_as_neutral": False,
                             "neutral_comparison_delta": None},
        "safeguards": {
            "shooting_double_counted": False, "hero_hunting_double_counted": False,
            "heroic_combat_assigned_to_offence": False,
            "deployment_frequency_inferred": False, "weapon_selection_inferred": False,
            "candidate_raw_density": None, "production_scoring_changed": False,
            "calibration_changed": False, "scenario_score": None,
            "dashboard_score": None, "promotion_authorised": False,
        },
    }


def view():
    return {
        "army_name": "Sample", "total_points": 700, "points_limit": 700,
        "model_count": 5, "metrics": {"offence": .5},
        "scenarios": [{"name": "scenario", "score": .5}],
        "provisional_capabilities": {"metrics": [{"metric_id": "offence", "rating": .5}]},
        "provisional_magic": {"display_only": True},
    }


def test_existing_response_schema_unchanged_without_optin():
    old = view()
    result = build_web_analysis_result(old)
    assert result["schema_version"] == "palantir-web-analysis-v1"
    assert "provisional_offence" not in result["analysis"]
    assert result["analysis"] == old


def test_opt_in_adds_one_diagnostic_property_only():
    old = view()
    expected = build_web_analysis_result(old)
    opt = {**old, "provisional_offence": row()}
    out = build_web_analysis_result(opt)
    assert {k:v for k,v in out["analysis"].items() if k != "provisional_offence"} == expected["analysis"]
    assert out["schema_version"] == expected["schema_version"]


def test_no_mutation_to_source():
    source = {**view(), "provisional_offence": row(alternatives=2)}
    before = deepcopy(source)
    build_web_analysis_result(source)
    assert source == before


def test_interval_is_not_coerced_to_point():
    x = build_provisional_offence_api_evidence(row(alternatives=2))
    assert x["neutral_melee"]["value"] is None
    assert x["neutral_melee"]["lower"] == 1.09
    assert x["neutral_melee"]["upper"] == 1.10


def test_qualified_point_retained():
    x = build_provisional_offence_api_evidence(row())
    assert x["neutral_melee"]["value"] == .69


def test_no_legacy_density_in_public_diagnostic():
    x = build_provisional_offence_api_evidence(row())
    assert "legacy_reference" not in x
    assert "density" not in x
    assert "comparison_delta" not in str(x)


def test_unknown_fields_not_transported():
    source = row()
    source["personal_notes"] = "not for API"
    source["conditional_capabilities"]["support"]["internal_token"] = "secret"
    output = build_provisional_offence_api_evidence(source)
    assert "personal_notes" not in json.dumps(output)
    assert "secret" not in json.dumps(output)


def test_json_roundtrip_and_no_nan():
    x = build_web_analysis_result({**view(), "provisional_offence": row()})
    assert x == json.loads(json.dumps(x, allow_nan=False))


def test_explicit_display_only():
    x = build_provisional_offence_api_evidence(row())
    assert x["status"] == "provisional_display_only"
    assert x["safeguards"]["promotion_authorised"] is False
    assert x["safeguards"]["candidate_raw_density"] is None


@pytest.mark.parametrize("section,field,value", [
    ("safeguards", "promotion_authorised", True),
    ("safeguards", "production_scoring_changed", True),
    ("safeguards", "calibration_changed", True),
    ("safeguards", "deployment_frequency_inferred", True),
    ("safeguards", "weapon_selection_inferred", True),
    ("safeguards", "candidate_raw_density", .4),
    ("safeguards", "scenario_score", .4),
    ("safeguards", "dashboard_score", .4),
    ("neutral_melee", "is_battlefield_forecast", True),
    ("neutral_melee", "is_overall_army_offence", True),
    ("conditional_capabilities.charge", "empirical_charge_frequency", .8),
    ("conditional_capabilities.support", "legally_available_support_opportunities", 1),
    ("conditional_capabilities.support", "additive_to_neutral_bar", True),
    ("conditional_capabilities.trapping", "combat_bonus_value", .2),
    ("conditional_capabilities.weapon_alternatives", "optimal_weapon_selected", True),
])
def test_invalid_promotion_or_tactical_claim_rejected(section, field, value):
    source = row()
    curr = source
    for token in section.split("."):
        curr = curr[token]
    curr[field] = value
    with pytest.raises(ValueError):
        build_provisional_offence_api_evidence(source)


@pytest.mark.parametrize("field,bad", [
    ("lower", -1), ("lower", float("nan")), ("upper", float("inf")),
    ("upper", .1), ("value", .5),
])
def test_invalid_neutral_bounds_rejected(field, bad):
    x = row()
    x["neutral_melee"][field] = bad
    with pytest.raises(ValueError):
        build_provisional_offence_api_evidence(x)


def test_interval_must_have_alternative_models():
    x = row()
    x["neutral_melee"]["value_type"] = "interval"
    with pytest.raises(ValueError):
        build_provisional_offence_api_evidence(x)


def test_alternatives_cannot_collapse_to_point():
    x = row(alternatives=2)
    x["neutral_melee"]["value"] = 1.1
    with pytest.raises(ValueError):
        build_provisional_offence_api_evidence(x)


def test_invalid_support_count_rejected():
    x = row()
    x["conditional_capabilities"]["support"]["equipped_models"] = 999
    with pytest.raises(ValueError):
        build_provisional_offence_api_evidence(x)


def test_optional_missing_data_is_not_fabricated():
    x = view()
    x["provisional_offence"] = None
    with pytest.raises(ValueError):
        build_web_analysis_result(x)


def test_required_historical_fields_still_required():
    x = view()
    del x["scenarios"]
    with pytest.raises(ValueError, match="Missing analysis field"):
        build_web_analysis_result(x)


def test_malformed_json_objects_still_rejected():
    x = view()
    x["metrics"] = {"bad": float("nan")}
    with pytest.raises(ValueError):
        build_web_analysis_result(x)
