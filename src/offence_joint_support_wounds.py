"""Project Palantír — DEV-082-A3-2H-3 joint spear support Duel + wound.

Authors: Edward Turns (Project Lead); OpenAI ChatGPT (Technical Lead).

A single explicitly configured *untrapped*, *uncharged*, *one-wound* combat.
Reuses DEV-082-A3-2H-2 for Duel probability, then applies each participant's
configured per-Strike wound probability separately. It never awards the
supporter a second independent combat. No production score or calibration.

Wound probability is conditional on winning the shared Duel. This module
does not model multiple-wound targets, situational rolls, Might, Heroics,
trapping, charge, weapon selection, attack-specific damage or
post-prevention effects; these are guarded/flagged rather than invented.
"""
from __future__ import annotations

from math import isfinite

from offence_explicit_support_combat import (
    ExplicitSupportContext, calculate_explicit_support_duel,
)

_EXCLUDED_RULES = frozenset({
    # Conditions/outcomes not currently carried by this deliberately narrow
    # baseline contract. Additional unknown rules remain a future audit.
    "BACKSTABBERS", "HATRED", "ANCIENT_ENEMIES", "I_AM_THE_MASTER",
    "MORGUL_BLADE", "TORTURER", "LETHAL_AIM",
})


def _check_probability(value, label):
    if type(value) not in (int, float) or not isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{label} must be a finite probability")
    return float(value)


def _has_unmodelled_rule(profile):
    rules = {assignment.rule.id for assignment in profile.effective_special_rules}
    return sorted(rules & _EXCLUDED_RULES)


def combine_independent_strike_failures(duel_win, strike_probabilities):
    """P(win shared Duel) × [1 - product(P(all eligible strikes fail))].

    Only valid for ordinary single-wound target, independent Strike attempts,
    and no additional post-prevention or conditional outcome effects.
    """
    win = _check_probability(duel_win, "duel_win")
    if not isinstance(strike_probabilities, (list, tuple)) or not strike_probabilities:
        raise ValueError("At least one eligible strike required")
    miss_all = 1.0
    for p in strike_probabilities:
        miss_all *= 1.0 - _check_probability(p, "strike_probability")
    return win * (1.0 - miss_all)


def calculate_explicit_joint_support_kill(
    fighter,
    supporter,
    *,
    fighter_id: str,
    supporter_id: str,
    context: ExplicitSupportContext,
    benchmark=None,
    duel_calculator=None,
    wound_calculator=None,
):
    """Read-only one-Duel, per-participant-Strike conditional evidence.

    ``duel_calculator``/``wound_calculator`` are injectable to contract-test
    the arithmetic. Production defaults reuse Palantír's verified resolvers.
    """
    from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
    from configured_profile import ConfiguredProfile
    from profiles import Profile

    bench = benchmark if benchmark is not None else DEFAULT_COMBAT_BENCHMARK
    if type(bench.wounds) is not int or bench.wounds != 1:
        raise ValueError("This stage supports only ordinary single-wound target")
    if type(bench.defence) is not int or not 1 <= bench.defence <= 10:
        raise ValueError("Invalid benchmark Defence")
    if _has_unmodelled_rule(fighter) or _has_unmodelled_rule(supporter):
        raise ValueError("Unmodelled conditional strike rule: audit separately")
    # Exclude cases where a default weapon selection would silently activate
    # a two-handed weapon modifier or conceal a real choice.
    for c in (fighter, supporter):
        gear = {w.id for w in c.effective_wargear}
        if "WG_TWO_HANDED_WEAPON" in gear:
            raise ValueError("Two-handed selection requires explicit weapon policy")
    duel = (duel_calculator or calculate_explicit_support_duel)(
        fighter, supporter, fighter_id=fighter_id, supporter_id=supporter_id,
        context=context, benchmark=bench,
    )
    if duel.get("status") != "conditional_duel_calculated":
        raise ValueError("Shared Duel contract was not satisfied")
    if duel.get("supporter_strikes_if_win") != 1:
        raise ValueError("Supporting model must contribute exactly one Strike")
    if duel.get("supporter_not_independent_combat") is not True:
        raise ValueError("Supporter cannot fight a second independent combat")
    if duel.get("production_scoring_changed") is not False:
        raise ValueError("Upstream scorer changed")

    if wound_calculator is None:
        from configured_wound_probability import calculate_configured_wound_probability
        wound_calculator = calculate_configured_wound_probability

    # Benchmark profile is deliberately ordinary with no Fate or special rules.
    opponent = ConfiguredProfile(profile=Profile(
        id="OFFENCE_JOINT_SUPPORT_BENCHMARK",
        name="Offence joint support benchmark",
        points=0, movement=6,
        fight=bench.fight, shooting="4+",
        strength=bench.strength, defence=bench.defence,
        attacks=bench.attacks, wounds=1,
        courage="4+", intelligence="4+",
        might=0, will=0, fate=0, max_in_army=0,
    ))
    # No trapping or charge assumed. Explicit WoundContext to prevent hidden
    # conditional rule activation based on missing context.
    from wound_context import WoundContext
    from wound_attack_type import WoundAttackType
    wound_context = WoundContext(
        defender_trapped=False,
        attack_type=WoundAttackType.STRIKE,
        attacker_charged=False,
    )
    p_fighter = _check_probability(
        float(wound_calculator(fighter, opponent, context=wound_context)),
        "fighter_wound_probability",
    )
    p_supporter = _check_probability(
        float(wound_calculator(supporter, opponent, context=wound_context)),
        "supporter_wound_probability",
    )
    fighter_strikes = duel.get("fighter_strikes_if_win")
    if type(fighter_strikes) is not int or fighter_strikes < 1:
        raise ValueError("Invalid fighter strike count")
    eligible = [p_fighter] * fighter_strikes + [p_supporter]
    win = _check_probability(duel.get("combined_duel_win_probability"), "duel_win")
    chance_any_wound_given_win = combine_independent_strike_failures(1.0, eligible)
    chance_kill = combine_independent_strike_failures(win, eligible)
    return {
        **duel,
        "stage": "DEV-082-A3-2H-3",
        "status": "conditional_joint_duel_and_wounds",
        "fighter_wound_probability_per_strike": p_fighter,
        "supporter_wound_probability_per_strike": p_supporter,
        "fighter_wound_evidence": "configured_wound_resolver",
        "supporter_wound_evidence": "configured_wound_resolver",
        "probability_at_least_one_wound_given_duel_win": chance_any_wound_given_win,
        "combined_kill_probability": chance_kill,
        "strike_distribution": {
            "fighter_eligible_strikes": fighter_strikes,
            "supporter_eligible_strikes": 1,
            "total_eligible_strikes": len(eligible),
        },
        "combat_assumptions": {
            "opponent_wounds": 1,
            "defender_trapped": False,
            "attacker_charged": False,
            "might_spent": 0,
            "heroic_actions": "none",
            "weapon_selection": "baseline_without_two_handed_option",
            "strike_attempts_independent_given_duel_win": True,
            "post_prevention_effects": "not_modelled",
        },
        "model_allocation": {
            **duel["model_allocation"],
            "independent_model_scores_added": False,
        },
        "candidate_raw_density": None,
        "production_scoring_changed": False,
        "calibration_changed": False,
        "dashboard_score": None,
        "scenario_score": None,
    }
