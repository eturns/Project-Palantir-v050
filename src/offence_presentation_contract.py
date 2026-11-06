"""Project Palantír — DEV-082-A3-2J-1 read-only Offence presentation contract.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Turn fully attributed A3-2I-5 evidence into *display-ready diagnostic data*.
No FastAPI mapper, frontend, production scorer, calibration, or scenario writes.
Display neutral melee and conditional opportunities as distinct dimensions.
Never promote the fully-charged legacy replay as an empirical bonus.
"""
from __future__ import annotations

from math import isclose, isfinite

TOL = 1e-9


def _value(x, field, *, positive=False):
    if type(x) not in (int, float) or not isfinite(x) or x < 0 or (positive and x <= 0):
        raise ValueError(f"{field}: expected finite nonnegative numeric value")
    return float(x)


def _matching(x, y, field):
    if not isclose(_value(x, field), _value(y, field), abs_tol=TOL, rel_tol=0):
        raise ValueError(f"{field}: attribution and neutral evidence mismatch")


def build_offence_presentation_row(attributed: dict, qualified: dict,
                                   coverage: dict) -> dict:
    """Fail closed unless same army and compatible I-5/I-4/I-2 provenance."""
    if (attributed.get("stage") != "DEV-082-A3-2I-5"
            or attributed.get("status") not in (
                "charged_replay_reconciled_full_profile_attribution",
                "charged_replay_reconciled_partial_attribution")
            or qualified.get("status") != "arithmetic_and_provenance_qualified"
            or coverage.get("status") != "neutral_coverage_qualified"):
        raise ValueError("Require qualified I-5, I-4 and I-2 inputs")
    key = attributed.get("key")
    if not isinstance(key, str) or not key or key != qualified.get("key") or key != coverage.get("key"):
        raise ValueError("Army identity mismatch")
    for name, source in (("attributed", attributed), ("qualified", qualified), ("coverage", coverage)):
        if (source.get("candidate_raw_density") is not None
                or source.get("production_scoring_changed") is not False
                or source.get("calibration_changed") is not False):
            raise ValueError(f"{name}: production/calibration safeguard breached")
    if (attributed.get("promotion_authorised") is not False
            or qualified.get("promote_to_dashboard") is not False
            or qualified.get("comparable_with_legacy_production_density") is not False
            or coverage.get("comparable_with_legacy_army_density") is not False
            or coverage.get("support_deployment_inferred") is not False
            or coverage.get("conditional_frequencies_inferred") is not False):
        raise ValueError("Unqualified promotion or tactical inference")
    if (attributed.get("legacy_charged_replay_matches_production") is not True
            or attributed.get("unexplained_profile_mismatches") != 0
            or attributed.get("neutral_mismatched_models") != 0):
        raise ValueError("Unreconciled profile or production replay")
    models = attributed.get("models")
    if type(models) is not int or models <= 0 or any(
        source.get("models") != models for source in (qualified, coverage)
    ):
        raise ValueError("Fielded model count mismatch")
    points = _value(attributed.get("points"), "army points", positive=True)
    _matching(points, qualified.get("points"), "points qualified")
    _matching(points, coverage.get("points"), "points coverage")
    qualified_models = qualified.get("neutral_reference_models")
    alternatives = qualified.get("weapon_alternative_models")
    if (type(qualified_models) is not int or type(alternatives) is not int
            or qualified_models < 0 or alternatives < 0
            or qualified_models + alternatives != models
            or qualified_models != coverage.get("neutral_reference_models")
            or alternatives != coverage.get("different_weapon_outcome_models")
            or alternatives != attributed.get("weapon_choice_unresolved_models")
            or qualified_models != attributed.get("neutral_matched_models")):
        raise ValueError("Neutral and unresolved-model populations disagree")
    lo = _value(qualified.get("neutral_density_lower_per_100pts"), "neutral lower")
    hi = _value(qualified.get("neutral_density_upper_per_100pts"), "neutral upper")
    if hi + TOL < lo:
        raise ValueError("Neutral range inverted")
    point = qualified.get("neutral_density_point_per_100pts")
    if alternatives:
        if point is not None or attributed.get("full_difference_attribution_possible") is not False:
            raise ValueError("Unresolved weapon options must remain interval-only")
    else:
        _matching(point, lo, "neutral point")
        _matching(hi, lo, "neutral point upper")
        if attributed.get("full_difference_attribution_possible") is not True:
            raise ValueError("Expected complete profile attribution")
    support_equipped = coverage.get("potential_support_equipped_models")
    if type(support_equipped) is not int or not 0 <= support_equipped <= models:
        raise ValueError("Support equipment census invalid")
    charged = _value(attributed.get("legacy_charged_replayed_density"), "charged replay")
    uncharged = _value(attributed.get("legacy_uncharged_replayed_density_reference_only"), "uncharged replay")
    known_effect = attributed.get("known_charge_parameter_contributions_per_100pts")
    if type(known_effect) not in (float, int) or not isfinite(known_effect):
        raise ValueError("Charge replay contribution not finite")
    if (not attributed.get("profile_rows_evidence")
            or len(attributed["profile_rows_evidence"]) != attributed.get("profile_rows")):
        raise ValueError("Missing source entry attribution")
    if attributed.get("metric_decision") != "retain_separate_neutral_melee_diagnostic_do_not_replace_composite_offence":
        raise ValueError("Unexpected metric decision")
    if qualified.get("candidate_qualification") != "diagnostic_only_not_production_approved":
        raise ValueError("Candidate qualification no longer diagnostic-only")
    # Legacy is a reference for *internal attribution*, never the neutral bar.
    return {
        "army_key": key,
        "stage": "DEV-082-A3-2J-1",
        "status": "diagnostic_presentation_contract_qualified",
        "visibility": "internal_preview_only_not_live_dashboard",
        "neutral_melee": {
            "label": "Neutral direct-melee density",
            "unit": "conditional expected single-wound defeats per 100 army points",
            "benchmark": "F4 S4 D6 A1 W1",
            "conditions": "one independent combat per model; uncharged; untrapped",
            "value_type": "interval" if alternatives else "point",
            "value": None if alternatives else lo,
            "lower": lo,
            "upper": hi,
            "qualifying_models": qualified_models,
            "unresolved_weapon_alternative_models": alternatives,
            "is_overall_army_offence": False,
            "is_battlefield_forecast": False,
        },
        "conditional_capabilities": {
            "charge": {
                "label": "Charge-sensitive scoring evidence",
                "evidence": "legacy_parameter_replay_only",
                "parameter_values_compared": [0.0, 1.0],
                "known_qualified_profile_contribution_per_100pts": float(known_effect),
                "full_profile_attribution": not bool(alternatives),
                "empirical_charge_frequency": None,
                "additive_to_neutral_bar": False,
            },
            "support": {
                "label": "Models carrying potential support equipment",
                "equipped_models": support_equipped,
                "legally_available_support_opportunities": None,
                "combat_bonus_value": None,
                "additive_to_neutral_bar": False,
            },
            "trapping": {
                "label": "Trapping potential",
                "frequency": None,
                "combat_bonus_value": None,
                "additive_to_neutral_bar": False,
            },
            "weapon_alternatives": {
                "label": "Unselected weapon alternatives",
                "affected_models": alternatives,
                "legal_selection_confirmed": False,
                "optimal_weapon_selected": False,
            },
        },
        "legacy_reference": {
            "label": "Existing production Offence Density (diagnostic reference)",
            "density": charged,
            "uncharged_replay_density": uncharged,
            "same_metric_as_neutral": False,
            "neutral_comparison_delta": None,
            "numerical_match_with_neutral": attributed.get("legacy_and_neutral_numerically_equal") is True,
        },
        "safeguards": {
            "shooting_double_counted": False,
            "hero_hunting_double_counted": False,
            "heroic_combat_assigned_to_offence": False,
            "deployment_frequency_inferred": False,
            "weapon_selection_inferred": False,
            "candidate_raw_density": None,
            "production_scoring_changed": False,
            "calibration_changed": False,
            "scenario_score": None,
            "dashboard_score": None,
            "promotion_authorised": False,
        },
    }


def build_offence_presentation_cohort(attribution: dict, qualification: dict,
                                      coverage: dict) -> dict:
    if (attribution.get("stage") != "DEV-082-A3-2I-5"
            or attribution.get("status") != "six_armies_attributed"
            or attribution.get("promotion_authorised") is not False
            or qualification.get("stage") != "DEV-082-A3-2I-4"
            or qualification.get("status") != "six_armies_arithmetic_audited"
            or coverage.get("stage") != "DEV-082-A3-2I-2"
            or coverage.get("status") != "six_armies_qualified"):
        raise ValueError("Require I-5, I-4, I-2 complete cohorts")
    for source in (attribution, qualification, coverage):
        if (source.get("candidate_raw_density") is not None
                or source.get("calibration_changed") is not False
                or source.get("production_scoring_changed") is not False):
            raise ValueError("Cohort freeze violated")
    collections = [s.get("rows") for s in (attribution, qualification, coverage)]
    if any(not isinstance(rows, list) or len(rows) != 6 for rows in collections):
        raise ValueError("Expected six rows in each cohort")
    keys = [[r.get("key") for r in rows] for rows in collections]
    if len(set(keys[0])) != 6 or not all(other == keys[0] for other in keys[1:]):
        raise ValueError("Cohort order/identity mismatch")
    cards = [build_offence_presentation_row(*triple) for triple in zip(*collections)]
    models = sum(r["neutral_melee"]["qualifying_models"] + r["neutral_melee"]["unresolved_weapon_alternative_models"] for r in cards)
    if models != attribution.get("models_examined") or models != qualification.get("models_examined") or models != coverage.get("models_examined"):
        raise ValueError("Model totals do not reconcile across cohorts")
    return {
        "stage": "DEV-082-A3-2J-1",
        "status": "six_armies_presentation_contract_qualified",
        "armies": len(cards),
        "models": models,
        "preview_rows": cards,
        "rendered_to_dashboard": False,
        "production_integration_authorised": False,
        "candidate_raw_density": None,
        "calibration_changed": False,
        "production_scoring_changed": False,
        "scenario_score": None,
        "dashboard_score": None,
    }
