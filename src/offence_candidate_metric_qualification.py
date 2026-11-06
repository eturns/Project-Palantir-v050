"""Project Palantír — DEV-082-A3-2I-4 candidate metric qualification audit.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Read-only, fail-closed arithmetic/provenance checks for A3-2I-3 against
A3-2I-2 and A3-2I-1. Reports exact legacy matches WITHOUT claiming the
two different metric contracts are equivalent. Does not infer charges,
support opportunities, trapping, alternative-weapon legality or tactics.
A numerical audit pass is NOT authorisation to replace production Offence.
"""
from __future__ import annotations

from math import fsum, isclose, isfinite

_TOL = 1e-10
_EXPECTED_SCOPES = {
    "comparison_scope": "uncharged_untrapped_independent_models_fixed_benchmark",
    "normalisation_unit":
        "conditional_expected_single_wound_defeats_per_100_army_points",
    "weapon_interval_scope":
        "unverified_alternative_scenario_envelope_not_optimal_selection",
}


def _num(value, field, *, prob=False, positive=False):
    if type(value) not in (int, float) or not isfinite(value):
        raise ValueError(f"{field} must be finite numeric evidence")
    if value < 0 or (positive and value == 0) or (prob and value > 1):
        raise ValueError(f"{field} outside its allowed range")
    return float(value)


def _close(a, b, field):
    if not isclose(_num(a, field + ".actual"), _num(b, field + ".expected"),
                   rel_tol=0, abs_tol=_TOL):
        raise ValueError(f"{field} does not reconcile")


def qualify_neutral_metric_army(numerical: dict, coverage: dict,
                               methodology: dict) -> dict:
    """Independently recompute counts, contributions and bounds per entry.

    The three inputs must represent the same army, including entry indices,
    quantities, model identities and points. No score or ranking is produced.
    """
    if (numerical.get("status") != "complete_conditional_reference"
            or coverage.get("status") != "neutral_coverage_qualified"
            or methodology.get("status") != "methodology_qualified"):
        raise ValueError("A3-2I-1/I-2/I-3 qualified inputs required")
    key = numerical.get("key")
    if not key or key != coverage.get("key") or key != methodology.get("key"):
        raise ValueError("Army identity mismatch")
    for tag, source in (("numerical", numerical),
                        ("coverage", coverage), ("methodology", methodology)):
        if (source.get("candidate_raw_density") is not None
                or source.get("production_scoring_changed") is not False
                or source.get("calibration_changed") is not False):
            raise ValueError(f"{tag}: production safeguards violated")
    if (numerical.get("comparable_with_legacy_production_density") is not False
            or coverage.get("comparable_with_legacy_army_density") is not False
            or methodology.get("legacy_and_neutral_scores_comparable") is not False
            or numerical.get("unresolved_options_selected") is not False
            or numerical.get("deployment_frequency_inferred") is not False
            or numerical.get("support_combat_benefit_included") is not False
            or numerical.get("charged_or_trapping_benefit_included") is not False
            or coverage.get("support_deployment_inferred") is not False
            or coverage.get("conditional_frequencies_inferred") is not False
            or methodology.get("conditional_weights") is not None):
        raise ValueError("Evidence incorrectly claims production comparability")
    for field, expected in _EXPECTED_SCOPES.items():
        if numerical.get(field) != expected:
            raise ValueError(f"Unexpected {field} provenance")
    models = numerical.get("models")
    if type(models) is not int or models <= 0 or any(
        s.get("models") != models for s in (coverage, methodology)
    ):
        raise ValueError("Model counts disagree between evidence stages")
    points = _num(numerical.get("points"), "points", positive=True)
    _close(points, coverage.get("points"), "coverage army points")
    _close(points, methodology.get("points"), "methodology army points")
    originals = coverage.get("profile_evidence")
    details = numerical.get("per_entry_evidence")
    if not isinstance(originals, list) or not isinstance(details, list):
        raise ValueError("Missing per-entry evidence")
    if len(originals) != len(details):
        raise ValueError("Per-entry rows lost or added")
    original_indices = set()
    qualified = alternative = unquantified = equivalent = 0
    fixed = []
    lower = []
    upper = []
    contributions = []
    for origin, evidence in zip(originals, details):
        idx = origin.get("entry_index")
        qty = origin.get("quantity")
        kind = origin.get("qualification")
        if (type(idx) is not int or idx < 1 or idx in original_indices
                or type(qty) is not int or qty <= 0):
            raise ValueError("Duplicate or malformed source entry")
        original_indices.add(idx)
        if any(evidence.get(f) != origin.get(f) for f in
               ("entry_index", "profile_id", "quantity", "qualification")):
            raise ValueError("Numerical entry does not match original evidence")
        if (origin.get("selected_weapon_id") is not None
                or origin.get("support_placement_inferred") is not False
                or evidence.get("selected_weapon_id") is not None):
            raise ValueError("Weapon/support choice inferred")
        current = origin.get("neutral_single_model_probability")
        bounds = evidence.get("conditional_range_per_model")
        if kind in ("single_option_neutral_reference",
                    "benchmark_equivalent_neutral_reference"):
            if (type(bounds) is not list or len(bounds) != 2
                    or evidence.get("neutral_probability_per_model") != current):
                raise ValueError("Qualified model probability provenance mismatch")
            p = _num(current, "qualified probability", prob=True)
            _close(bounds[0], p, "qualified lower")
            _close(bounds[1], p, "qualified upper")
            fixed.append(qty * p)
            lo = hi = p
            qualified += qty
            if kind == "benchmark_equivalent_neutral_reference":
                equivalent += qty
                weapon = origin.get("weapon_option_evidence")
                if (not isinstance(weapon, dict)
                        or weapon.get("all_comparison_states_equivalent") is not True
                        or weapon.get("weapon_legality") != "not_verified"):
                    raise ValueError("Equivalent-option provenance lost")
        elif kind == "different_weapon_outcomes_unresolved":
            if (current is not None
                    or evidence.get("neutral_probability_per_model") is not None
                    or type(bounds) is not list or len(bounds) != 2):
                raise ValueError("Unresolved weapon selection improperly resolved")
            weapon = origin.get("weapon_option_evidence")
            if (not isinstance(weapon, dict)
                    or weapon.get("weapon_legality") != "not_verified"
                    or weapon.get("all_comparison_states_equivalent") is not False):
                raise ValueError("Unresolved alternative provenance lost")
            expected = weapon.get("uncharged_probability_range")
            if not isinstance(expected, list) or len(expected) != 2:
                raise ValueError("Unresolved weapon bounds missing")
            lo = _num(expected[0], "alternative lower", prob=True)
            hi = _num(expected[1], "alternative upper", prob=True)
            if hi < lo:
                raise ValueError("Alternative interval inverted")
            _close(bounds[0], lo, "alternative lower")
            _close(bounds[1], hi, "alternative upper")
            alternative += qty
        else:
            raise ValueError("Unquantified/unsupported entry blocks qualification")
        lower.append(qty * lo)
        upper.append(qty * hi)
        contributions.append({
            "entry_index": idx, "profile_id": origin["profile_id"],
            "quantity": qty, "qualification": kind,
            "conditional_expected_defeats_lower": qty * lo,
            "conditional_expected_defeats_upper": qty * hi,
        })
    if (qualified + alternative + unquantified != models
            or qualified != coverage.get("neutral_reference_models")
            or alternative != coverage.get("different_weapon_outcome_models")
            or equivalent != coverage.get("new_benchmark_equivalent_models")
            or numerical.get("neutral_reference_models") != qualified
            or numerical.get("weapon_alternative_models") != alternative
            or numerical.get("unquantified_models") != 0):
        raise ValueError("Population/qualification counts do not reconcile")
    fixed_total, low_total, high_total = (
        fsum(fixed), fsum(lower), fsum(upper)
    )
    scale = 100 / points
    for k, computed in (
        ("fixed_qualified_expected_defeats", fixed_total),
        ("conditional_total_expected_defeats_lower", low_total),
        ("conditional_total_expected_defeats_upper", high_total),
        ("neutral_direct_melee_density_lower_per_100pts", low_total * scale),
        ("neutral_direct_melee_density_upper_per_100pts", high_total * scale),
    ):
        _close(numerical.get(k), computed, k)
    if alternative:
        if numerical.get("neutral_direct_melee_density_point_per_100pts") is not None:
            raise ValueError("Interval cannot be collapsed to point score")
    else:
        _close(numerical.get("neutral_direct_melee_density_point_per_100pts"),
               low_total * scale, "neutral point")
    old = _num(methodology.get("legacy_raw_density_production_reference_only"),
               "legacy reference")
    neutral_low = low_total * scale
    neutral_high = high_total * scale
    exact_match = (
        isclose(old, neutral_low, rel_tol=0, abs_tol=_TOL)
        and isclose(old, neutral_high, rel_tol=0, abs_tol=_TOL)
    )
    return {
        "key": key,
        "status": "arithmetic_and_provenance_qualified",
        "models": models,
        "points": points,
        "neutral_reference_models": qualified,
        "weapon_alternative_models": alternative,
        "per_entry_contribution_count": len(contributions),
        "neutral_density_lower_per_100pts": neutral_low,
        "neutral_density_upper_per_100pts": neutral_high,
        "neutral_density_point_per_100pts": (
            neutral_low if alternative == 0 else None),
        "legacy_production_reference_only": old,
        "legacy_neutral_numerically_equal": exact_match,
        "legacy_match_interpretation": (
            "numerical_coincidence_or_matching_model_contributions;"
            "mechanical_attribution_not_yet_verified" if exact_match
            else "different_outputs_different_contracts_no_delta_inferred"
        ),
        "entry_contributions": contributions,
        "candidate_qualification": "diagnostic_only_not_production_approved",
        "candidate_raw_density": None,
        "comparable_with_legacy_production_density": False,
        "supports_army_wide_tactical_forecast": False,
        "promote_to_dashboard": False,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }


def audit_neutral_metric_cohort(numerical_cohort: dict,
                                coverage_cohort: dict,
                                methodology_cohort: dict) -> dict:
    if any(
        cohort.get("status") != expected or cohort.get("stage") != stage
        or cohort.get("candidate_raw_density") is not None
        or cohort.get("production_scoring_changed") is not False
        or cohort.get("calibration_changed") is not False
        for cohort, expected, stage in (
            (numerical_cohort, "six_armies_compared", "DEV-082-A3-2I-3"),
            (coverage_cohort, "six_armies_qualified", "DEV-082-A3-2I-2"),
            (methodology_cohort, "six_armies_qualified", "DEV-082-A3-2I-1"),
        )
    ):
        raise ValueError("Three complete frozen source cohorts required")
    cohorts = (numerical_cohort, coverage_cohort, methodology_cohort)
    rows = [c.get("rows") for c in cohorts]
    if any(not isinstance(r, list) or len(r) != 6 for r in rows):
        raise ValueError("Six rows in each cohort required")
    keys = [[r.get("key") for r in rowset] for rowset in rows]
    if any(len(set(ks)) != 6 for ks in keys) or keys[0] != keys[1] or keys[0] != keys[2]:
        raise ValueError("Six source cohorts must be in the same unique order")
    qualified = []
    for numerical, coverage, methodology in zip(*rows):
        qualified.append(qualify_neutral_metric_army(
            numerical, coverage, methodology
        ))
    if (numerical_cohort.get("models_examined") !=
            sum(r["models"] for r in qualified)):
        raise ValueError("Cohort model totals do not reconcile")
    return {
        "stage": "DEV-082-A3-2I-4",
        "status": "six_armies_arithmetic_audited",
        "armies_audited": 6,
        "models_examined": sum(r["models"] for r in qualified),
        "neutral_reference_models": sum(r["neutral_reference_models"] for r in qualified),
        "weapon_alternative_models": sum(r["weapon_alternative_models"] for r in qualified),
        "legacy_exact_matches_requiring_attribution": [
            r["key"] for r in qualified if r["legacy_neutral_numerically_equal"]
        ],
        "rows": qualified,
        "promotion_decision": "blocked_pending_mechanical_attribution_and_tactical_scope",
        "rankings_generated": False,
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
