"""Project Palantír — DEV-082-A3-2I-5 mechanical attribution audit.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

Replays the EXISTING per-profile scoring function twice (charge_probability
0.0 and 1.0), reconciles its charged scores to the frozen legacy total,
and aligns each profile with the I4 independent, neutral probability interval.
Do not interpret replay differences as actual tabletop charge frequencies.
No modified game mechanics, army scores, calibration, or website output.
"""
from __future__ import annotations

from math import fsum, isclose, isfinite

TOL = 1e-9


def _value(x, name, *, upper=None):
    if type(x) not in (float, int) or not isfinite(x) or x < 0 or (upper is not None and x > upper):
        raise ValueError(f"Invalid {name}: expected finite nonnegative value")
    return float(x)


def _near(a, b):
    return isclose(a, b, abs_tol=TOL, rel_tol=0)


def replay_legacy_profile_states(army, scorer=None) -> list[dict]:
    """Call production scorer for the current configured entry, no writeback.

    The charged setting is the historical default of
    calculate_army_offensive_output_density (charge_probability=1.0).
    The uncharged replay is *not* automatically identical to A3-2I neutral.
    """
    if scorer is None:
        from profile_offensive_combat_score import calculate_profile_offensive_combat_score
        from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
        scorer = lambda profile, p: calculate_profile_offensive_combat_score(
            profile, DEFAULT_COMBAT_BENCHMARK, charge_probability=p)
    rows = []
    for idx, entry in enumerate(army.entries, start=1):
        if not entry.counts_as_model:
            continue
        if entry.configured_profile is None:
            raise ValueError("Fielded entry without configured profile")
        qty = entry.quantity
        if type(qty) is not int or qty < 1:
            raise ValueError("Invalid fielded quantity")
        profile_id = entry.configured_profile.profile.id
        uncharged = _value(scorer(entry.configured_profile, 0.0), "uncharged replay", upper=1)
        charged = _value(scorer(entry.configured_profile, 1.0), "charged replay", upper=1)
        rows.append({
            "entry_index": idx, "profile_id": profile_id, "quantity": qty,
            "legacy_uncharged_per_model": uncharged,
            "legacy_charged_per_model": charged,
            "charge_parameter_effect_per_model": charged - uncharged,
        })
    if not rows or sum(r["quantity"] for r in rows) != army.model_count():
        raise ValueError("Replay model count does not reconcile")
    return rows


def attribute_army_neutral_difference(qualified: dict, replay: list[dict], *,
                                      production_check: float | None = None) -> dict:
    """Attribute differences where evidence is comparable; otherwise flag.

    A 'replay_no_charge_matches_neutral' match is a mechanical *result*
    for that entry only; it does not establish rules completeness, tactical
    legality, or permission to promote the neutral metric to production.
    """
    if qualified.get("status") != "arithmetic_and_provenance_qualified":
        raise ValueError("Require completed I4 arithmetic and provenance audit")
    if (qualified.get("candidate_raw_density") is not None
            or qualified.get("promote_to_dashboard") is not False
            or qualified.get("production_scoring_changed") is not False
            or qualified.get("calibration_changed") is not False
            or qualified.get("comparable_with_legacy_production_density") is not False):
        raise ValueError("Read-only qualification contract violated")
    points = _value(qualified.get("points"), "army points")
    if points <= 0:
        raise ValueError("Points must be positive")
    expected = qualified.get("entry_contributions")
    if not isinstance(replay, list) or not isinstance(expected, list) or len(replay) != len(expected):
        raise ValueError("One-to-one per-entry evidence required")
    seen = set()
    detail = []
    charge_weighted = []
    nocharge_weighted = []
    matches = mismatches = alternatives = matched_models = mismatched_models = 0
    sum_charge_attributed = []
    for old, neutral in zip(replay, expected):
        idx = neutral.get("entry_index")
        qty = neutral.get("quantity")
        if idx in seen or type(idx) is not int or type(qty) is not int or qty <= 0:
            raise ValueError("Invalid or repeated model entry")
        seen.add(idx)
        if any(old.get(f) != neutral.get(f) for f in ("entry_index", "profile_id", "quantity")):
            raise ValueError("Replay does not match neutral model identity/order")
        n_low = _value(neutral.get("conditional_expected_defeats_lower"), "neutral lower")
        n_high = _value(neutral.get("conditional_expected_defeats_upper"), "neutral upper")
        if n_low > n_high + TOL or n_high > qty + TOL:
            raise ValueError("Invalid neutral per-entry probability contributions")
        lo = _value(old.get("legacy_uncharged_per_model"), "replay uncharged", upper=1)
        hi = _value(old.get("legacy_charged_per_model"), "replay charged", upper=1)
        effect = old.get("charge_parameter_effect_per_model")
        if type(effect) not in (float, int) or not isfinite(effect) or not _near(effect, hi - lo):
            raise ValueError("Inconsistent charge parameter replay")
        charge_weighted.append(qty * hi)
        nocharge_weighted.append(qty * lo)
        classification = neutral.get("qualification")
        is_option = classification == "different_weapon_outcomes_unresolved"
        if is_option:
            alternatives += qty
            state = "weapon_selection_unresolved_no_causal_attribution"
            aligned = None
        elif classification in ("single_option_neutral_reference", "benchmark_equivalent_neutral_reference"):
            if not _near(n_low, n_high):
                raise ValueError("Qualified fixed reference must be a point")
            aligned = _near(qty * lo, n_low)
            if aligned:
                matches += 1
                matched_models += qty
                state = ("charge_parameter_difference_isolated" if not _near(lo, hi)
                         else "same_replay_result_at_both_charge_parameters")
                sum_charge_attributed.append(qty * (hi - lo))
            else:
                mismatches += 1
                mismatched_models += qty
                state = "neutral_vs_uncharged_replay_mismatch_requires_rule_trace"
        else:
            raise ValueError("Unsupported neutral qualification")
        detail.append({
            "entry_index": idx, "profile_id": neutral["profile_id"], "quantity": qty,
            "neutral_expected_defeats_lower": n_low,
            "neutral_expected_defeats_upper": n_high,
            "legacy_replay_uncharged_per_model": lo,
            "legacy_replay_charged_per_model": hi,
            "charge_parameter_effect_per_model": hi - lo,
            "replay_uncharged_matches_neutral": aligned,
            "attribution": state,
        })
    if sum(r["quantity"] for r in detail) != qualified.get("models"):
        raise ValueError("Model population mismatch")
    if alternatives != qualified.get("weapon_alternative_models"):
        raise ValueError("Weapon-alternative model population mismatch")
    charge_total = fsum(charge_weighted)
    nocharge_total = fsum(nocharge_weighted)
    charge_density = charge_total * 100 / points
    nocharge_density = nocharge_total * 100 / points
    legacy_reference = _value(qualified.get("legacy_production_reference_only"), "legacy reference")
    production_reconciled = _near(charge_density, legacy_reference)
    if production_check is not None:
        direct = _value(production_check, "direct production scorer")
        if not _near(direct, charge_density):
            raise ValueError("Legacy charge replay differs from production scoring function")
    if not production_reconciled:
        raise ValueError("Legacy charged replay does not match frozen production reference")
    # Do not infer an aggregate *net causal difference* across mismatched
    # entries or unresolved weapon variants. No cancellation-based attribution.
    full_attribution = not mismatches and not alternatives
    matches_at_both = bool(qualified.get("legacy_neutral_numerically_equal"))
    return {
        "key": qualified["key"],
        "stage": "DEV-082-A3-2I-5",
        "status": "charged_replay_reconciled_partial_attribution" if not full_attribution
                  else "charged_replay_reconciled_full_profile_attribution",
        "models": qualified["models"], "points": points,
        "profile_rows": len(detail),
        "neutral_matched_models": matched_models,
        "neutral_mismatched_models": mismatched_models,
        "weapon_choice_unresolved_models": alternatives,
        "legacy_charged_replayed_density": charge_density,
        "legacy_uncharged_replayed_density_reference_only": nocharge_density,
        "legacy_charged_replay_matches_production": True,
        "legacy_and_neutral_numerically_equal": matches_at_both,
        "full_difference_attribution_possible": full_attribution,
        "known_charge_parameter_contributions_per_100pts": fsum(sum_charge_attributed) * 100 / points,
        "unexplained_profile_mismatches": mismatches,
        "explanation_policy": (
            "charge_parameter_replay_is_not_empirical_charge_frequency;"
            "potential_special_rule_and_weapon_behaviour_requires_manual_review"
        ),
        "profile_rows_evidence": detail,
        "metric_decision": "retain_separate_neutral_melee_diagnostic_do_not_replace_composite_offence",
        "production_scoring_changed": False,
        "calibration_changed": False,
        "candidate_raw_density": None,
        "dashboard_score": None,
        "scenario_score": None,
        "promotion_authorised": False,
    }


def attribute_six_armies(qualified: dict, armies: list, *, scorer=None,
                           production_calculator=None) -> dict:
    if qualified.get("status") != "six_armies_arithmetic_audited" or len(qualified.get("rows", [])) != 6:
        raise ValueError("Need complete A3-2I-4 cohort")
    if len(armies) != 6 or qualified.get("models_examined") != sum(r["models"] for r in qualified["rows"]):
        raise ValueError("Six army cohort/model count mismatch")
    keys = [r["key"] for r in qualified["rows"]]
    if len(set(keys)) != 6:
        raise ValueError("Duplicate army key")
    results = []
    for source, army in zip(qualified["rows"], armies):
        if army.model_count() != source["models"]:
            raise ValueError("Imported army model count mismatch")
        replay = replay_legacy_profile_states(army, scorer=scorer)
        production_value = production_calculator(army) if production_calculator is not None else None
        results.append(attribute_army_neutral_difference(
            source, replay, production_check=production_value))
    return {
        "stage": "DEV-082-A3-2I-5", "status": "six_armies_attributed",
        "armies_audited": 6,
        "models_examined": sum(r["models"] for r in results),
        "full_profile_attribution_armies": [r["key"] for r in results if r["full_difference_attribution_possible"]],
        "partial_attribution_armies": [r["key"] for r in results if not r["full_difference_attribution_possible"]],
        "rows": results,
        "candidate_raw_density": None, "dashboard_score": None,
        "scenario_score": None, "calibration_changed": False,
        "production_scoring_changed": False,
        "promotion_authorised": False,
        "metric_decision": "keep_neutral_direct_melee_separate_from_conditional_capabilities",
    }
