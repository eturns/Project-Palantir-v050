"""Opt-in Goblin Crew combat evidence for the existing offence pipeline.

The caller supplies the conditional post-Duel context.  Standard scoreboard
calls pass no context, so provisional scoring cannot silently change.
"""
from fractions import Fraction

from gundabad_goblin_crew import (
    GoblinCrewCombatContext,
    can_make_goblin_crew_strikes,
    is_gundabad_catapult_troll,
    resolve_goblin_crew_strikes,
)


def combined_goblin_crew_kill_probability(
    attacker,
    *,
    troll_wound_distribution: tuple[Fraction, ...],
    troll_wounds_per_success: int,
    target_wounds: int,
    target_defence: int,
    context: GoblinCrewCombatContext,
) -> Fraction:
    """P(target slain | Duel won), with full uniform D6 Crew distribution.

    Troll successful Strikes may each inflict multiple wounds; Crew successful
    Strikes each inflict one wound. Fate, saves and other defensive states are
    outside this limited-context evidence. No extra Duel dice are introduced.
    """
    if not is_gundabad_catapult_troll(attacker):
        raise ValueError("Goblin Crew combat evidence requires the Catapult Troll.")
    if not isinstance(context, GoblinCrewCombatContext) or not context.combat_won:
        raise ValueError("Expected an explicit post-Duel winning context.")
    if not context.troll_strikes_resolved and not context.combat_ended_by_brutal_power_attack:
        raise ValueError("Resolve Troll Strikes before Goblin Crew.")
    if type(troll_wounds_per_success) is not int or troll_wounds_per_success < 1:
        raise ValueError("Invalid Troll wound multiplier.")
    if type(target_wounds) is not int or target_wounds < 1:
        raise ValueError("Invalid target Wounds.")
    if type(target_defence) is not int or not 1 <= target_defence <= 10:
        raise ValueError("Invalid target Defence.")
    if not troll_wound_distribution or sum(troll_wound_distribution) != 1:
        raise ValueError("Troll wound distribution must sum to one.")
    if any(p < 0 or p > 1 for p in troll_wound_distribution):
        raise ValueError("Invalid Troll wound probability.")

    baseline = sum(
        (p for successes, p in enumerate(troll_wound_distribution)
         if successes * troll_wounds_per_success >= target_wounds),
        Fraction(0),
    )
    if not can_make_goblin_crew_strikes(attacker, context):
        return baseline

    total = Fraction(0)
    for d6 in range(1, 7):
        crew = resolve_goblin_crew_strikes(
            attacker, context, d6_strikes=d6, target_defence=target_defence
        )
        for troll_successes, troll_probability in enumerate(troll_wound_distribution):
            for crew_wounds, crew_probability in enumerate(crew.wound_count_distribution):
                if troll_successes * troll_wounds_per_success + crew_wounds >= target_wounds:
                    total += troll_probability * crew_probability / 6
    return total
