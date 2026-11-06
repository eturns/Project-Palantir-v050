"""Project Palantír — DEV-082-A3-2J-2 diagnostic Offence API adapter.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Strict, optional and display-only serializer for a *prequalified* J-1
presentation record. Does not calculate the army, infer scenario states,
select weapons, or authorise candidate score promotion.
"""
from __future__ import annotations

import json
from math import isfinite


def _number(value, name):
    if type(value) not in (float, int) or not isfinite(value) or value < 0:
        raise ValueError(f"Invalid {name}")
    return float(value)


def build_provisional_offence_api_evidence(row: dict) -> dict:
    """Return a strict subset of J-1 evidence safe for public JSON transport.

    Fails closed if a source claims score promotion, inferred combat frequency,
    or battlefield forecasts. Unknown source fields are NOT forwarded.
    """
    if not isinstance(row, dict) or row.get("stage") != "DEV-082-A3-2J-1":
        raise ValueError("Qualified DEV-082-A3-2J-1 row required")
    if (row.get("status") != "diagnostic_presentation_contract_qualified"
            or row.get("visibility") != "internal_preview_only_not_live_dashboard"):
        raise ValueError("Unqualified presentation row")
    key = row.get("army_key")
    if not isinstance(key, str) or not key or len(key) > 100:
        raise ValueError("Invalid army identity")
    safe = row.get("safeguards")
    if not isinstance(safe, dict) or any(safe.get(flag) is not False for flag in (
        "shooting_double_counted", "hero_hunting_double_counted",
        "heroic_combat_assigned_to_offence", "deployment_frequency_inferred",
        "weapon_selection_inferred", "production_scoring_changed",
        "calibration_changed", "promotion_authorised",
    )) or any(safe.get(field) is not None for field in (
        "candidate_raw_density", "scenario_score", "dashboard_score",
    )):
        raise ValueError("Production freeze or attribution invariant violated")
    neutral = row.get("neutral_melee")
    caps = row.get("conditional_capabilities")
    legacy = row.get("legacy_reference")
    if not all(isinstance(x, dict) for x in (neutral, caps, legacy)):
        raise ValueError("Missing required diagnostic sections")
    if (neutral.get("benchmark") != "F4 S4 D6 A1 W1"
            or neutral.get("conditions") != "one independent combat per model; uncharged; untrapped"
            or neutral.get("is_overall_army_offence") is not False
            or neutral.get("is_battlefield_forecast") is not False):
        raise ValueError("Incorrect neutral scope")
    low, high = (_number(neutral.get(name), name) for name in ("lower", "upper"))
    if high < low:
        raise ValueError("Neutral interval inverted")
    reference_models = neutral.get("qualifying_models")
    alternative_models = neutral.get("unresolved_weapon_alternative_models")
    if (type(reference_models) is not int or reference_models < 0
            or type(alternative_models) is not int or alternative_models < 0
            or reference_models + alternative_models == 0):
        raise ValueError("Invalid model census")
    value_type = neutral.get("value_type")
    if alternative_models:
        if value_type != "interval" or neutral.get("value") is not None:
            raise ValueError("Unresolved weapons require an interval")
        point = None
    else:
        if value_type != "point":
            raise ValueError("Qualified neutral reference requires point")
        point = _number(neutral.get("value"), "neutral point")
        if abs(point - low) > 1e-9 or abs(high - low) > 1e-9:
            raise ValueError("Point is inconsistent with reference")
    charge = caps.get("charge")
    support = caps.get("support")
    trap = caps.get("trapping")
    weapons = caps.get("weapon_alternatives")
    if not all(isinstance(x, dict) for x in (charge, support, trap, weapons)):
        raise ValueError("Missing conditional capability evidence")
    if (charge.get("evidence") != "legacy_parameter_replay_only"
            or charge.get("parameter_values_compared") != [0.0, 1.0]
            or charge.get("empirical_charge_frequency") is not None
            or support.get("legally_available_support_opportunities") is not None
            or support.get("combat_bonus_value") is not None
            or trap.get("frequency") is not None
            or trap.get("combat_bonus_value") is not None
            or weapons.get("legal_selection_confirmed") is not False
            or weapons.get("optimal_weapon_selected") is not False
            or any(c.get("additive_to_neutral_bar") is not False for c in
                   (charge, support, trap))):
        raise ValueError("Unqualified conditional capability or implied additivity")
    equipped = support.get("equipped_models")
    affected = weapons.get("affected_models")
    if (type(equipped) is not int or equipped < 0
            or equipped > reference_models + alternative_models
            or type(affected) is not int or affected != alternative_models):
        raise ValueError("Conditional capability model counts inconsistent")
    effect = charge.get("known_qualified_profile_contribution_per_100pts")
    if type(effect) not in (float, int) or not isfinite(effect):
        raise ValueError("Invalid charge replay sensitivity")
    if charge.get("full_profile_attribution") is not (alternative_models == 0):
        raise ValueError("Unresolved alternatives must remain partial attribution")
    if legacy.get("same_metric_as_neutral") is not False or legacy.get("neutral_comparison_delta") is not None:
        raise ValueError("Legacy metric incorrectly conflated with neutral")
    _number(legacy.get("density"), "legacy density")
    _number(legacy.get("uncharged_replay_density"), "legacy uncharged replay")
    out = {
        "stage": "DEV-082-A3-2J-2",
        "status": "provisional_display_only",
        "army_key": key,
        "visibility": "diagnostic_not_calibrated_not_overall_offence",
        "neutral_melee": {
            "unit": neutral.get("unit"),
            "benchmark": "F4 S4 D6 A1 W1",
            "conditions": neutral["conditions"],
            "value_type": value_type,
            "value": point,
            "lower": low, "upper": high,
            "qualifying_models": reference_models,
            "unresolved_weapon_alternative_models": alternative_models,
            "is_overall_army_offence": False,
            "is_battlefield_forecast": False,
        },
        "conditional_capabilities": {
            "charge": {
                "evidence": "legacy_parameter_replay_only",
                "known_qualified_profile_contribution_per_100pts": float(effect),
                "full_profile_attribution": alternative_models == 0,
                "empirical_charge_frequency": None,
                "additive_to_neutral_bar": False,
            },
            "support": {
                "equipped_models": equipped,
                "legally_available_support_opportunities": None,
                "combat_bonus_value": None,
                "additive_to_neutral_bar": False,
            },
            "trapping": {
                "frequency": None, "combat_bonus_value": None,
                "additive_to_neutral_bar": False,
            },
            "weapon_alternatives": {
                "affected_models": alternative_models,
                "legal_selection_confirmed": False,
                "optimal_weapon_selected": False,
            },
        },
        "safeguards": {
            "production_scoring_changed": False,
            "calibration_changed": False,
            "scenario_score": None,
            "dashboard_score": None,
            "candidate_raw_density": None,
            "promotion_authorised": False,
        },
    }
    if out["neutral_melee"]["unit"] != "conditional expected single-wound defeats per 100 army points":
        raise ValueError("Unexpected neutral measurement unit")
    return json.loads(json.dumps(out, allow_nan=False))
