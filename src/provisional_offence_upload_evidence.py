"""Project Palantír — DEV-082-A3-2J-3 per-upload Offence diagnostics.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Uses the SAME Army object returned by main.run_analysis_workflow. No fixture
lookup, second import, score promotion, or scenario/calibration modification.
Failure to qualify is a display-only status; never substitute a zero score.
"""
from __future__ import annotations

from army import Army

MAX_MODELS = 300
MAX_FIELD_ENTRIES = 150


def _unqualified(reason: str, army: Army | None) -> dict:
    if reason not in {
        "invalid_army", "empty_army", "analysis_limit_exceeded",
        "unsupported_or_unverified_configuration",
    }:
        raise ValueError("Invalid diagnostic failure category")
    count = None
    if isinstance(army, Army):
        try:
            number = army.model_count()
            if type(number) is int and number >= 0:
                count = number
        except (ValueError, AttributeError, TypeError):
            pass
    return {
        "stage": "DEV-082-A3-2J-3",
        "status": "not_qualified",
        "reason_code": reason,
        "army_key": "user_upload",
        "models": count,
        "neutral_melee": None,
        "conditional_capabilities": None,
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "scenario_score": None,
        "dashboard_score": None,
        "promotion_authorised": False,
    }


def calculate_uploaded_army_offence_evidence(army: Army) -> dict:
    """Return J-1 qualified presentation OR J-3 unqualified placeholder.

    All calculations are independent diagnostics using existing profilers.
    Exceptions from unsupported mechanical contexts are not exposed to API
    clients; no partial score from an unqualified calculation is published.
    """
    if not isinstance(army, Army):
        return _unqualified("invalid_army", None)
    try:
        models = army.model_count()
        field_entries = sum(1 for entry in army.entries if entry.counts_as_model)
        if models == 0:
            return _unqualified("empty_army", army)
        if (type(models) is not int or models < 0 or models > MAX_MODELS
                or field_entries > MAX_FIELD_ENTRIES):
            return _unqualified("analysis_limit_exceeded", army)

        # Lazy-load the shadow DEV-082 modules only after the ordinary web
        # analysis succeeded and its real Army object is available.
        from offence_trapping_benchmark import build_trapping_qualified_offence_report
        from offence_weapon_qualification import build_weapon_qualified_offence_report
        from offence_explicit_army_aggregation import make_fielded_offence_roster
        from offence_aggregation_methodology import classify_army_methodology
        from offence_multi_weapon_audit import audit_multi_weapon_report
        from offence_weapon_resolution_policy import qualify_multi_weapon_cohort
        from offence_neutral_baseline_completeness import qualify_neutral_baseline_completeness
        from offence_neutral_mechanical_comparison import compare_neutral_mechanical_army
        from offence_candidate_metric_qualification import qualify_neutral_metric_army
        from offence_mechanical_attribution import (
            replay_legacy_profile_states, attribute_army_neutral_difference,
        )
        from offence_presentation_contract import build_offence_presentation_row
        from army_offence_capability import calculate_army_offensive_output_density

        key = "user_upload"
        methodology = classify_army_methodology(
            key, build_trapping_qualified_offence_report(army),
            make_fielded_offence_roster(army),
        )
        weapon_audit = audit_multi_weapon_report(
            build_weapon_qualified_offence_report(army), key=key,
        )
        weapon_cohort = {
            "stage": "DEV-082-A3-2G-1", "status": "complete",
            "armies_expected": 1, "rows": [weapon_audit],
            "multi_weapon_models": weapon_audit["multiple_weapon_models"],
            "candidate_raw_density": None,
            "production_scoring_changed": False, "calibration_changed": False,
        }
        weapon_qualification = qualify_multi_weapon_cohort(weapon_cohort)
        if (weapon_qualification.get("status") != "complete"
                or weapon_qualification.get("armies_qualified") != 1):
            return _unqualified("unsupported_or_unverified_configuration", army)
        coverage = qualify_neutral_baseline_completeness(
            methodology, weapon_qualification["rows"][0]
        )
        numerical = compare_neutral_mechanical_army(coverage)
        qualified = qualify_neutral_metric_army(numerical, coverage, methodology)
        replay = replay_legacy_profile_states(army)
        attributed = attribute_army_neutral_difference(
            qualified, replay,
            production_check=calculate_army_offensive_output_density(
                army, charge_probability=1.0,
            ),
        )
        return build_offence_presentation_row(attributed, qualified, coverage)
    except Exception:
        # Public path fails closed. Never return a fabricated probability or
        # expose profile IDs, user lists, or private traceback in API errors.
        return _unqualified("unsupported_or_unverified_configuration", army)
