"""Project Palantír — DEV-082-A3-2I-2 neutral baseline coverage gate.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Extends A3-2I-1 using verified A3-2G-2 *benchmark* equivalence.
This does NOT verify weapon legality, choose a weapon, add spear-support
benefits, estimate deployment, or produce an army Offence Density score.
The old charged production density remains a DIFFERENT metric.
"""
from __future__ import annotations

from math import isfinite

TOLERANCE = 1e-12
COMPARISON_STATES = (
    "uncharged", "charged", "eligible_cavalry_charge",
)


def _prob(value, label):
    if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{label}: invalid probability")
    return float(value)


def qualify_neutral_baseline_completeness(
    methodology: dict, weapon_policy: dict
) -> dict:
    """Merge row-aligned I1 single-option evidence and G2 option comparisons.

    Match repeated profile/configuration rows in original report order rather
    than using profile_id as a key (Iron Hills has repeated IH_WR entries).
    """
    if methodology.get("status") != "methodology_qualified":
        raise ValueError("Expected a qualified A3-2I-1 army")
    if weapon_policy.get("status") != "qualified":
        raise ValueError("Expected qualified A3-2G-2 weapon army")
    if methodology.get("key") != weapon_policy.get("key"):
        raise ValueError("Army identities do not match")
    if methodology.get("models") != weapon_policy.get("models"):
        raise ValueError("Army model counts do not match")
    if methodology.get("multiple_weapon_models_unselected") != weapon_policy.get("multiple_weapon_models"):
        raise ValueError("Multiple-option model counts disagree")
    for record in (methodology,):
        if (record.get("candidate_raw_density") is not None
                or record.get("calibration_changed") is not False
                or record.get("production_scoring_changed") is not False
                or record.get("baseline_army_score") is not None
                or record.get("legacy_and_neutral_scores_comparable") is not False):
            raise ValueError("Methodology scoring safeguards violated")
    if methodology.get("conditional_weights") is not None:
        raise ValueError("No conditional frequencies may be applied")
    evidence = methodology.get("profile_evidence")
    options = weapon_policy.get("profile_resolutions")
    if not isinstance(evidence, list) or not isinstance(options, list):
        raise ValueError("Missing detailed profile evidence")
    if weapon_policy.get("status_model_counts") is None:
        raise ValueError("Missing weapon classification totals")
    used = 0
    resolved, different, existing, unknown = 0, 0, 0, 0
    new_rows = []
    for row in evidence:
        qty = row.get("quantity")
        profile_id = row.get("profile_id")
        old_status = row.get("qualification")
        value = row.get("neutral_single_model_probability")
        if type(qty) is not int or qty <= 0:
            raise ValueError("Bad evidence quantity")
        if row.get("selected_weapon_id") is not None or row.get("support_placement_inferred") is not False:
            raise ValueError("A weapon or support deployment was selected")
        if old_status == "reference_available_not_final_score":
            value = _prob(value, "single-option baseline")
            status = "single_option_neutral_reference"
            existing += qty
            detail = None
        elif old_status == "option_choice_not_assumed":
            if value is not None:
                raise ValueError("I1 must not select a multi-weapon reference")
            if used >= len(options):
                raise ValueError("Missing G2 multi-option row")
            option = options[used]
            used += 1
            if option.get("profile_id") != profile_id or option.get("quantity") != qty:
                raise ValueError("G2 multi-option row order/profile/quantity mismatch")
            if (option.get("selected_weapon_id") is not None
                    or option.get("automatic_choice_made") is not False
                    or option.get("weapon_legality") != "not_verified"
                    or option.get("eligible_for_unconditional_army_density") is not False
                    or option.get("benchmark_equivalence_scope") != "ordinary_single_wound_direct_melee_only"):
                raise ValueError("G2 option evidence inferred weapon choice or legality")
            comp = option.get("state_comparisons")
            if not isinstance(comp, dict) or set(comp) != set(COMPARISON_STATES):
                raise ValueError("Missing or unexpected comparison states")
            differences = []
            for state in COMPARISON_STATES:
                c = comp[state]
                low = _prob(c.get("minimum_probability"), state + ".minimum")
                high = _prob(c.get("maximum_probability"), state + ".maximum")
                spread = _prob(c.get("difference"), state + ".difference")
                if high + TOLERANCE < low or abs(high-low-spread) > TOLERANCE:
                    raise ValueError("Option comparison differs from recorded range")
                equivalent = high-low <= TOLERANCE
                if c.get("benchmark_equivalent") is not equivalent:
                    raise ValueError("G2 equivalence disagrees with numerical evidence")
                differences.append(not equivalent)
            policy_status = option.get("policy_status")
            if policy_status == "benchmark_equivalent_options" and not any(differences):
                # This is a property of the benchmark, NOT a weapon selection.
                value = _prob(comp["uncharged"]["minimum_probability"], "neutral equivalent")
                resolved += qty
                status = "benchmark_equivalent_neutral_reference"
            elif policy_status == "different_conditional_outcomes" and any(differences):
                value = None
                different += qty
                status = "different_weapon_outcomes_unresolved"
            else:
                raise ValueError("G2 policy classification inconsistent")
            detail = {
                "candidate_weapon_ids": list(option.get("candidate_weapon_ids", [])),
                "support_capability_ids": list(option.get("support_capability_ids", [])),
                "uncharged_probability_range": [
                    comp["uncharged"]["minimum_probability"],
                    comp["uncharged"]["maximum_probability"],
                ],
                "all_comparison_states_equivalent": not any(differences),
                "weapon_legality": "not_verified",
            }
        elif old_status == "melee_reference_unresolved":
            if value is not None:
                raise ValueError("Unresolved reference must not have probability")
            status = "unresolved"
            detail = None
            unknown += qty
        else:
            raise ValueError("Unexpected A3-2I-1 qualification state")
        new_rows.append({
            "entry_index": row.get("entry_index"),
            "profile_id": profile_id,
            "quantity": qty,
            "qualification": status,
            "neutral_single_model_probability": value,
            "selected_weapon_id": None,
            "support_placement_inferred": False,
            "weapon_option_evidence": detail,
        })
    if used != len(options):
        raise ValueError("Unused or duplicated G2 weapon rows")
    total = existing + resolved + different + unknown
    if total != methodology.get("models"):
        raise ValueError("Qualified, unresolved model populations do not reconcile")
    if existing != methodology.get("neutral_baseline_reference_models"):
        raise ValueError("I1 existing neutral coverage mismatch")
    if resolved + different != methodology.get("multiple_weapon_models_unselected"):
        raise ValueError("G2 multiple-option coverage mismatch")
    expected_classes = weapon_policy["status_model_counts"]
    if (resolved != expected_classes.get("benchmark_equivalent_options", 0)
            or different != expected_classes.get("different_conditional_outcomes", 0)):
        raise ValueError("G2 class totals mismatch")
    count = existing + resolved
    return {
        "key": methodology["key"],
        "status": "neutral_coverage_qualified",
        "points": methodology["points"],
        "models": total,
        "previous_single_option_models": existing,
        "new_benchmark_equivalent_models": resolved,
        "neutral_reference_models": count,
        "different_weapon_outcome_models": different,
        "other_unresolved_models": unknown,
        "coverage_ratio": count / total,
        "potential_support_equipped_models": methodology["potential_support_equipped_models"],
        "profile_evidence": new_rows,
        "baseline_army_score": None,
        "candidate_raw_density": None,
        "comparable_with_legacy_army_density": False,
        "selected_weapon_id": None,
        "support_deployment_inferred": False,
        "conditional_frequencies_inferred": False,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }


def build_neutral_baseline_cohort(
    *, fixtures, loader, methodology_reporter, weapon_reporter
) -> dict:
    """Six-army diagnostics with failed fixtures visible, never silently omitted.

    methodology_reporter(army) returns a validated I1 army row.
    weapon_reporter(army,key) returns one validated G2 army row.
    """
    rows = []
    for key, fixture in fixtures:
        try:
            army = loader(fixture)
            method = methodology_reporter(army, key)
            options = weapon_reporter(army, key)
            result = qualify_neutral_baseline_completeness(method, options)
        except Exception as exc:
            result = {"key": key, "status": "blocked",
                      "reason": f"{type(exc).__name__}: {exc}"}
        rows.append(result)
    qualified = [r for r in rows if r["status"] == "neutral_coverage_qualified"]
    return {
        "stage": "DEV-082-A3-2I-2",
        "status": ("six_armies_qualified"
                   if len(rows) == 6 and len(qualified) == 6 else "incomplete"),
        "armies_qualified": len(qualified),
        "armies_expected": len(rows),
        "models_examined": sum(r["models"] for r in qualified),
        "neutral_reference_models": sum(r["neutral_reference_models"] for r in qualified),
        "new_benchmark_equivalent_models": sum(r["new_benchmark_equivalent_models"] for r in qualified),
        "different_weapon_outcome_models": sum(r["different_weapon_outcome_models"] for r in qualified),
        "other_unresolved_models": sum(r["other_unresolved_models"] for r in qualified),
        "rows": rows,
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
