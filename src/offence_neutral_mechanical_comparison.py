"""Project Palantír — DEV-082-A3-2I-3 neutral direct-melee comparison.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Read-only numerical evidence for an UNCHARGED, UNTRAPPED, single-wound,
independent-model direct-melee benchmark. These values are NOT the old charged
production density, not a deployment prediction and not a new Offence score.

All qualified models contribute their unique benchmark outcome. For remaining
weapon choices with non-equivalent outcomes, the explicit range of possible
per-model outcomes is retained. Endpoints are mathematical *scenario envelopes*,
not verified legal/optimal loadouts and not an estimated probability distribution.
"""
from __future__ import annotations

from math import fsum, isfinite

TOLERANCE = 1e-12


def _finite(value, label, *, upper=None):
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{label} requires finite numeric evidence")
    if value < 0 or (upper is not None and value > upper):
        raise ValueError(f"{label} outside accepted bounds")
    return float(value)


def compare_neutral_mechanical_army(coverage: dict) -> dict:
    """Calculate an explicitly scoped range, preserving unresolved options.

    This function deliberately cannot produce ``candidate_raw_density``.
    """
    if coverage.get("status") != "neutral_coverage_qualified":
        raise ValueError("Require verified A3-2I-2 neutral coverage")
    if (coverage.get("candidate_raw_density") is not None
            or coverage.get("baseline_army_score") is not None
            or coverage.get("production_scoring_changed") is not False
            or coverage.get("calibration_changed") is not False
            or coverage.get("comparable_with_legacy_army_density") is not False
            or coverage.get("support_deployment_inferred") is not False
            or coverage.get("conditional_frequencies_inferred") is not False
            or coverage.get("selected_weapon_id") is not None):
        raise ValueError("Frozen no-selection/read-only contract violated")
    key = coverage.get("key")
    if not isinstance(key, str) or not key.strip():
        raise ValueError("Army cohort key missing")
    points = _finite(coverage.get("points"), "points")
    if points <= 0:
        raise ValueError("Army points must be positive")
    population = coverage.get("models")
    if type(population) is not int or population <= 0:
        raise ValueError("Invalid army model population")
    rows = coverage.get("profile_evidence")
    if not isinstance(rows, list) or not rows:
        raise ValueError("Detailed A3-2I-2 model evidence required")

    seen_entries = set()
    fixed_contributions = []
    low_contributions = []
    high_contributions = []
    detailed = []
    counts = {"single_option_neutral_reference": 0,
              "benchmark_equivalent_neutral_reference": 0,
              "different_weapon_outcomes_unresolved": 0,
              "unresolved": 0}
    for row in rows:
        entry_id, profile_id, qty = (row.get("entry_index"),
                                     row.get("profile_id"), row.get("quantity"))
        if type(entry_id) is not int or entry_id < 1 or entry_id in seen_entries:
            raise ValueError("Missing/duplicate fielded entry index")
        seen_entries.add(entry_id)
        if not isinstance(profile_id, str) or not profile_id.strip():
            raise ValueError("Missing profile ID")
        if type(qty) is not int or qty <= 0:
            raise ValueError("Invalid fielded quantity")
        if (row.get("selected_weapon_id") is not None
                or row.get("support_placement_inferred") is not False):
            raise ValueError("Weapon selection/support deployment inferred")
        status = row.get("qualification")
        if status not in counts:
            raise ValueError("Unsupported neutral qualification")
        counts[status] += qty
        prob = row.get("neutral_single_model_probability")
        weapon = row.get("weapon_option_evidence")
        if status in ("single_option_neutral_reference",
                      "benchmark_equivalent_neutral_reference"):
            p = _finite(prob, "neutral reference", upper=1)
            if status == "benchmark_equivalent_neutral_reference":
                if not isinstance(weapon, dict):
                    raise ValueError("Equivalent weapon evidence absent")
                if (weapon.get("all_comparison_states_equivalent") is not True
                        or weapon.get("weapon_legality") != "not_verified"):
                    raise ValueError("Equivalence/legality safeguards missing")
                bounds = weapon.get("uncharged_probability_range")
                if not isinstance(bounds, list) or len(bounds) != 2:
                    raise ValueError("Equivalent probability bounds absent")
                a, b = (_finite(x, "equivalent bound", upper=1) for x in bounds)
                if abs(a - b) > TOLERANCE or abs(p - a) > TOLERANCE:
                    raise ValueError("Neutral reference differs from equivalent options")
            fixed_contributions.append(p * qty)
            lower = upper = p
        elif status == "different_weapon_outcomes_unresolved":
            if prob is not None or not isinstance(weapon, dict):
                raise ValueError("Different options cannot have selected baseline")
            if (weapon.get("weapon_legality") != "not_verified"
                    or weapon.get("all_comparison_states_equivalent") is not False):
                raise ValueError("Different weapon options incorrectly qualified")
            bounds = weapon.get("uncharged_probability_range")
            if not isinstance(bounds, list) or len(bounds) != 2:
                raise ValueError("Unresolved options require lower and upper bounds")
            lower, upper = (_finite(x, "unresolved probability", upper=1)
                            for x in bounds)
            if upper + TOLERANCE < lower:
                raise ValueError("Unresolved option bounds reversed")
        else:
            # Genuinely unquantified evidence cannot be assigned a zero and
            # must suppress the entire army's numerical range.
            if prob is not None:
                raise ValueError("Unknown reference cannot have probability")
            lower = upper = None
        if lower is not None:
            low_contributions.append(lower * qty)
            high_contributions.append(upper * qty)
        detailed.append({
            "entry_index": entry_id, "profile_id": profile_id, "quantity": qty,
            "qualification": status, "neutral_probability_per_model": prob,
            "conditional_range_per_model": ([lower, upper] if lower is not None else None),
            "selected_weapon_id": None,
        })

    if sum(counts.values()) != population:
        raise ValueError("All fielded models must reconcile")
    fixed_count = (counts["single_option_neutral_reference"]
                   + counts["benchmark_equivalent_neutral_reference"])
    different_count = counts["different_weapon_outcomes_unresolved"]
    unknown_count = counts["unresolved"]
    if (fixed_count != coverage.get("neutral_reference_models")
            or different_count != coverage.get("different_weapon_outcome_models")
            or unknown_count != coverage.get("other_unresolved_models")
            or counts["benchmark_equivalent_neutral_reference"]
               != coverage.get("new_benchmark_equivalent_models")
            or abs(fixed_count / population - coverage.get("coverage_ratio", -1)) > TOLERANCE):
        raise ValueError("A3-2I-2 coverage totals inconsistent")
    if len(low_contributions) != len(rows) - sum(
        r["qualification"] == "unresolved" for r in detailed
    ):
        raise ValueError("Missing numeric evidence for a qualified row")
    scale = 100.0 / points
    fixed = fsum(fixed_contributions)
    fully_quantified = unknown_count == 0
    lower_sum = fsum(low_contributions) if fully_quantified else None
    upper_sum = fsum(high_contributions) if fully_quantified else None
    point = (lower_sum if fully_quantified and different_count == 0 else None)
    return {
        "key": key, "status": ("complete_conditional_reference" if fully_quantified
                               else "incomplete_numeric_coverage"),
        "points": points, "models": population,
        "neutral_reference_models": fixed_count,
        "weapon_alternative_models": different_count,
        "unquantified_models": unknown_count,
        "fixed_qualified_expected_defeats": fixed,
        "conditional_total_expected_defeats_lower": lower_sum,
        "conditional_total_expected_defeats_upper": upper_sum,
        "neutral_direct_melee_density_lower_per_100pts": (
            lower_sum * scale if fully_quantified else None),
        "neutral_direct_melee_density_upper_per_100pts": (
            upper_sum * scale if fully_quantified else None),
        "neutral_direct_melee_density_point_per_100pts": (
            point * scale if point is not None else None),
        "normalisation_unit": "conditional_expected_single_wound_defeats_per_100_army_points",
        "comparison_scope": "uncharged_untrapped_independent_models_fixed_benchmark",
        "weapon_interval_scope": "unverified_alternative_scenario_envelope_not_optimal_selection",
        "unresolved_options_selected": False,
        "deployment_frequency_inferred": False,
        "support_combat_benefit_included": False,
        "charged_or_trapping_benefit_included": False,
        "comparable_with_legacy_production_density": False,
        "per_entry_evidence": detailed,
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }


def compare_six_armies(coverage_report: dict) -> dict:
    """Never rank across incomplete six-army input or infer a replacement score."""
    if (coverage_report.get("stage") != "DEV-082-A3-2I-2"
            or coverage_report.get("status") != "six_armies_qualified"
            or coverage_report.get("armies_expected") != 6
            or coverage_report.get("armies_qualified") != 6
            or coverage_report.get("candidate_raw_density") is not None
            or coverage_report.get("production_scoring_changed") is not False
            or coverage_report.get("calibration_changed") is not False):
        raise ValueError("Requires complete frozen six-army A3-2I-2 evidence")
    rows = coverage_report.get("rows")
    if not isinstance(rows, list) or len(rows) != 6:
        raise ValueError("Exactly six qualified army rows required")
    keys = [row.get("key") for row in rows]
    if len(set(keys)) != 6:
        raise ValueError("Six cohort army identities must be unique")
    compared = [compare_neutral_mechanical_army(row) for row in rows]
    # Ranking by an arbitrary midpoint would silently pick a weapon outcome.
    # Present ranges in fixture order; never rank unresolved intervals.
    return {
        "stage": "DEV-082-A3-2I-3",
        "status": ("six_armies_compared" if all(
            row["status"] == "complete_conditional_reference" for row in compared
        ) else "numeric_coverage_incomplete"),
        "armies_compared": len(compared),
        "armies_expected": 6,
        "models_examined": sum(row["models"] for row in compared),
        "neutral_reference_models": sum(row["neutral_reference_models"] for row in compared),
        "weapon_alternative_models": sum(row["weapon_alternative_models"] for row in compared),
        "unquantified_models": sum(row["unquantified_models"] for row in compared),
        "rows": compared,
        "rankings_generated": False,
        "production_comparisons_generated": False,
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
