"""Project Palantír — DEV-082-A3-2G-2 benchmark weapon resolution policy.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead)

Read-only classification of A3-2G-1 conditional weapon evidence.
Equivalent outcomes do NOT establish equivalent battlefield utility or legality.
Different outcomes do NOT license selecting the higher value.
"""
from __future__ import annotations

from collections import Counter
from math import isfinite

from offence_multi_weapon_audit import STATES

TOLERANCE = 1e-12
SUPPORT_RELEVANT_IDS = frozenset({"WG_SPEAR", "WG_WAR_SPEAR"})


def classify_weapon_audit_row(row: dict) -> dict:
    """Classify all listed choices across the three current combat states."""
    quantity = row.get("quantity")
    if type(quantity) is not int or quantity < 1:
        raise ValueError("Weapon row quantity must be a positive integer")
    profile_id = row.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id:
        raise ValueError("Missing profile ID")
    options = row.get("alternatives")
    ids = row.get("candidate_weapon_ids")
    if not isinstance(options, list) or len(options) < 2:
        raise ValueError("At least two option outcomes required")
    if not isinstance(ids, list) or len(ids) != len(options) or len(set(ids)) != len(ids):
        raise ValueError("Candidate weapons are missing or duplicated")
    if {option.get("weapon_id") for option in options} != set(ids):
        raise ValueError("Explicit option identities do not match candidates")
    if row.get("legal_option_verified") is not False:
        raise ValueError("This stage must not assert weapon legality")
    if row.get("selection_status") != "requires_legal_option_and_tactical_policy":
        raise ValueError("Unexpected selected weapon policy")

    per_state = {}
    for state in STATES:
        values = []
        for option in options:
            if option.get("battlefield_legality") != "not_verified" or option.get("player_choice") != "not_inferred":
                raise ValueError("Weapon legality or player choice was inferred")
            probabilities = option.get("conditional_probabilities")
            if not isinstance(probabilities, dict):
                raise ValueError("Conditional probabilities absent")
            value = probabilities.get(state)
            if type(value) not in (float, int) or not isfinite(value) or not 0 <= value <= 1:
                raise ValueError("Weapon probability must be finite in [0, 1]")
            values.append(float(value))
        minimum, maximum = min(values), max(values)
        spread = maximum - minimum
        supplied = row.get("outcome_comparison", {}).get(state)
        if not isinstance(supplied, dict):
            raise ValueError("Original comparison state missing")
        for field, actual in (("minimum", minimum), ("maximum", maximum), ("spread", spread)):
            prior = supplied.get(field)
            if type(prior) not in (int, float) or not isfinite(prior) or abs(prior - actual) > TOLERANCE:
                raise ValueError("Original comparison conflicts with explicit options")
        if supplied.get("outcomes_differ") is not (spread > TOLERANCE):
            raise ValueError("Original difference classification disagrees")
        per_state[state.replace("_probability", "")] = {
            "minimum_probability": minimum,
            "maximum_probability": maximum,
            "difference": spread,
            "benchmark_equivalent": spread <= TOLERANCE,
        }

    equivalent = all(part["benchmark_equivalent"] for part in per_state.values())
    support_ids = sorted(set(ids) & SUPPORT_RELEVANT_IDS)
    return {
        "profile_id": profile_id,
        "quantity": quantity,
        "candidate_weapon_ids": list(ids),
        "policy_status": ("benchmark_equivalent_options" if equivalent
                          else "different_conditional_outcomes"),
        "state_comparisons": per_state,
        "benchmark_equivalence_scope": "ordinary_single_wound_direct_melee_only",
        "support_capability_ids": support_ids,
        "support_attack_contribution": "not_evaluated" if support_ids else "not_applicable_to_catalogued_options",
        "weapon_legality": "not_verified",
        "selected_weapon_id": None,
        "automatic_choice_made": False,
        "eligible_for_unconditional_army_density": False,
    }


def qualify_multi_weapon_cohort(audit: dict) -> dict:
    """Summarise A3-2G-1; blocked input causes an incomplete result, not a pass."""
    if audit.get("stage") != "DEV-082-A3-2G-1":
        raise ValueError("Expected DEV-082-A3-2G-1 audit")
    if (audit.get("candidate_raw_density") is not None
            or audit.get("production_scoring_changed") is not False
            or audit.get("calibration_changed") is not False):
        raise ValueError("Audit must be read-only")
    rows = audit.get("rows")
    if not isinstance(rows, list) or len(rows) != audit.get("armies_expected"):
        raise ValueError("Incorrect army population")
    result_rows = []
    counts = Counter()
    for army_row in rows:
        key = army_row.get("key")
        if army_row.get("status") != "audited":
            result_rows.append({"key": key, "status": "blocked", "reason": army_row.get("reason", "not_audited")})
            continue
        if (army_row.get("automatic_selection_made") is not False
                or army_row.get("legality_verified") is not False
                or army_row.get("candidate_raw_density") is not None
                or army_row.get("production_scoring_changed") is not False
                or army_row.get("calibration_changed") is not False):
            raise ValueError("Army violates read-only unselected weapon contract")
        detailed_rows = army_row.get("profile_audits")
        if not isinstance(detailed_rows, list):
            raise ValueError("Missing weapon audit rows")
        classifications = [classify_weapon_audit_row(entry) for entry in detailed_rows]
        total = sum(entry["quantity"] for entry in classifications)
        if total != army_row.get("multiple_weapon_models"):
            raise ValueError("Weapon model count mismatch")
        local = Counter()
        for entry in classifications:
            local[entry["policy_status"]] += entry["quantity"]
            counts[entry["policy_status"]] += entry["quantity"]
        result_rows.append({
            "key": key, "status": "qualified",
            "models": army_row.get("models"),
            "multiple_weapon_models": total,
            "status_model_counts": dict(sorted(local.items())),
            "profile_resolutions": classifications,
        })
    complete = len(result_rows) > 0 and all(row["status"] == "qualified" for row in result_rows)
    if complete:
        if sum(row["multiple_weapon_models"] for row in result_rows) != audit.get("multi_weapon_models"):
            raise ValueError("Cross-army weapon model count mismatch")
    return {
        "stage": "DEV-082-A3-2G-2",
        "status": "complete" if complete else "incomplete",
        "armies_qualified": sum(row["status"] == "qualified" for row in result_rows),
        "armies_expected": len(result_rows),
        "multiple_weapon_models": sum(row.get("multiple_weapon_models", 0) for row in result_rows),
        "classification_model_counts": dict(sorted(counts.items())),
        "rows": result_rows,
        "policy": "benchmark_equivalence_only_no_legality_or_auto_choice",
        "candidate_raw_density": None,
        "calibration_changed": False,
        "production_scoring_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
