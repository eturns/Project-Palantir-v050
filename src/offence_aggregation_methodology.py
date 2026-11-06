"""Project Palantír — DEV-082-A3-2I-1 aggregation methodology gate.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Read-only decision evidence. Existing legacy density is NOT the uncharged
neutral-baseline calculation. A qualified single-option conditional result
is NOT a fielded combat deployment or proof of legal use in every situation.
No numerical candidate metric, calibration change, or dashboard integration.
"""
from __future__ import annotations

from math import isfinite

METHOD = {
    "baseline": "explicit_uncharged_untrapped_single_wound_direct_melee",
    "baseline_unit": "conditional_probability_per_independent_model_vs_fixed_benchmark",
    "normalisation_proposal": "sum_qualified_per_model_mechanical_outputs_times_100_divided_by_army_points",
    "normalisation_status": "proposed_not_integrated",
    "conditional_supplements": (
        "charged", "eligible_cavalry_charge", "trapped",
        "explicit_supporting_combat", "alternative_weapon_selection",
    ),
    "unknown_weight_policy": "no_frequency_estimated_or_implicitly_zeroed",
    "support_policy": "joint_combat_only_one_model_allocation_per_opportunity",
    "score_policy": "no_candidate_while_coverage_or_context_unresolved",
    "no_double_count": (
        "shooting_excluded", "hero_hunting_excluded",
        "heroic_combat_excluded", "supporter_not_independent_fighter",
    ),
}


def _check(value, label, *, probability=False):
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if value < 0 or (probability and value > 1):
        raise ValueError(f"{label} outside accepted bounds")
    return float(value)


def classify_army_methodology(key: str, evidence: dict, roster: dict) -> dict:
    """Classify a complete A3-2E report and H4 roster without choosing weapons.

    Only a single catalogued melee option with its own explicit uncharged /
    untrapped probability is 'reference_available'. No probability is used as
    a new whole-army score, and benchmark equivalence does not prove legality.
    """
    if not isinstance(key, str) or not key.strip():
        raise ValueError("Cohort key required")
    if evidence.get("stage") != "DEV-082-A3-2E":
        raise ValueError("A3-2E trapping/weapon report required")
    if (evidence.get("production_scoring_changed") is not False
            or evidence.get("calibration_changed") is not False
            or evidence.get("candidate_raw_density") is not None
            or evidence.get("comparable") is not False
            or evidence.get("trapping_frequency_assumed") is not False):
        raise ValueError("Source evidence violates frozen read-only contract")
    if roster.get("allocation_status") != "not_inferred":
        raise ValueError("Roster allocation must remain uninferred")
    roster_rows = roster.get("models")
    if not isinstance(roster_rows, list):
        raise ValueError("Roster rows missing")
    model_count = evidence.get("fielded_models")
    if type(model_count) is not int or model_count < 1:
        raise ValueError("Invalid fielded model count")
    if roster.get("model_count") != model_count or len(roster_rows) != model_count:
        raise ValueError("Report/roster population mismatch")
    expected_ids = [r.get("model_id") for r in roster_rows]
    if len(set(expected_ids)) != model_count:
        raise ValueError("Duplicated roster identities")
    points = _check(evidence.get("army_points"), "army_points")
    if points <= 0:
        raise ValueError("Army points must be positive")
    previous = _check(evidence.get("legacy_raw_density"), "legacy_raw_density")
    rows = evidence.get("profile_rows")
    if not isinstance(rows, list):
        raise ValueError("Missing profile rows")
    qualified, multiple, unresolved = 0, 0, 0
    representative = []
    entry_groups = {}
    for model in roster_rows:
        entry_groups.setdefault(model["entry_index"], []).append(model)
    ordered_entries = sorted(entry_groups)
    if len(rows) != len(ordered_entries):
        raise ValueError("Report/roster entry count mismatch")
    for row, actual_idx in zip(rows, ordered_entries):
        qty = row.get("quantity")
        profile_id = row.get("profile_id")
        if type(qty) is not int or qty < 1 or not isinstance(profile_id, str):
            raise ValueError("Invalid fielded row")
        grouped = entry_groups[actual_idx]
        if len(grouped) != qty or any(m["profile_id"] != profile_id for m in grouped):
            raise ValueError("Evidence row does not match ordered roster entry")
        w = row.get("weapon_options")
        if not isinstance(w, dict):
            raise ValueError("Weapon status required")
        state = w.get("status")
        trapped = row.get("trapping_benchmark")
        t_status = row.get("trapping_benchmark_status")
        if state == "single_recognised_option":
            if t_status != "paired_conditional_outcomes" or not isinstance(trapped, dict):
                raise ValueError("Single option needs three explicit trapping states")
            states = trapped.get("conditional_combat_states")
            if not isinstance(states, list) or len(states) != 3:
                raise ValueError("Three contextual states required")
            uncharged = [s for s in states if s.get("state") == "uncharged"]
            if len(uncharged) != 1:
                raise ValueError("Missing neutral uncharged state")
            probability = _check(uncharged[0].get("untrapped_probability"),
                                 "uncharged/untrapped", probability=True)
            qualified += qty
            outcome = "reference_available_not_final_score"
        elif state == "multiple_options":
            if trapped is not None:
                raise ValueError("No default trapped state for unresolved weapon selection")
            multiple += qty
            probability = None
            outcome = "option_choice_not_assumed"
        else:
            unresolved += qty
            probability = None
            outcome = "melee_reference_unresolved"
        representative.append({
            "entry_index": actual_idx, "profile_id": profile_id,
            "quantity": qty, "qualification": outcome,
            "neutral_single_model_probability": probability,
            "selected_weapon_id": None,
            "support_placement_inferred": False,
        })
    if qualified + multiple + unresolved != model_count:
        raise ValueError("Qualified model groups do not reconcile")
    potential_support = roster.get("potential_support_equipped_count")
    if type(potential_support) is not int or not 0 <= potential_support <= model_count:
        raise ValueError("Bad potential supporter count")
    return {
        "key": key, "status": "methodology_qualified",
        "points": points, "models": model_count,
        "legacy_raw_density_production_reference_only": previous,
        "neutral_baseline_reference_models": qualified,
        "multiple_weapon_models_unselected": multiple,
        "other_unresolved_models": unresolved,
        "potential_support_equipped_models": potential_support,
        "neutral_baseline_coverage_ratio": qualified / model_count,
        "profile_evidence": representative,
        "baseline_army_score": None,
        "candidate_raw_density": None,
        "legacy_and_neutral_scores_comparable": False,
        "conditional_weights": None,
        "score_blockers": [
            "weapon_selection_legality_not_verified",
            "support_deployment_frequency_unknown",
            "charge_and_trap_frequency_unknown",
            "no_complete_army_level_mechanical_aggregation_yet",
        ],
        "calibration_changed": False,
        "production_scoring_changed": False,
    }


def build_methodology_cohort(*, fixtures, loader, reporter, roster_builder) -> dict:
    rows = []
    for key, fixture in fixtures:
        try:
            army = loader(fixture)
            result = classify_army_methodology(key, reporter(army), roster_builder(army))
        except Exception as exc:
            result = {"key": key, "status": "blocked",
                      "reason": f"{type(exc).__name__}: {exc}"}
        rows.append(result)
    ready = [r for r in rows if r["status"] == "methodology_qualified"]
    return {
        "stage": "DEV-082-A3-2I-1",
        "status": "six_armies_qualified" if len(rows) == 6 and len(ready) == 6 else "incomplete",
        "armies_qualified": len(ready), "armies_expected": len(rows),
        "models_examined": sum(r["models"] for r in ready),
        "neutral_reference_models": sum(r["neutral_baseline_reference_models"] for r in ready),
        "weapon_choice_unresolved_models": sum(r["multiple_weapon_models_unselected"] for r in ready),
        "potential_support_equipped_models": sum(r["potential_support_equipped_models"] for r in ready),
        "methodology": METHOD,
        "rows": rows,
        "candidate_raw_density": None, "dashboard_score": None,
        "scenario_score": None, "calibration_changed": False,
        "production_scoring_changed": False,
    }
