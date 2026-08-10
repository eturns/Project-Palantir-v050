"""
Project Palantír
================

File:
    duel_probability.py

Purpose:
    Calculates raw Duel-roll probabilities.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-039 – Combat Engine Foundation
"""

# ============================================================================
# Imports
# ============================================================================

from itertools import product

from duel_probability_result import DuelProbabilityResult
from profiles import Profile

from duel_might import (
    DuelMightStrategy,
    resolve_duel_might,
)

from heroic_strike import generate_duel_fight_outcomes

from combat_side import CombatSide
from duel_modifier import (
    DuelModifier,
    apply_duel_modifier_to_rolls,
)
# ============================================================================
# Functions
# ============================================================================

def calculate_raw_duel_probability(
    attacker_attacks: int,
    defender_attacks: int,
    attacker_reroll_available: bool = False,
    defender_reroll_available: bool = False,
    attacker_might_available: int = 0,
    defender_might_available: int = 0,
    attacker_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    defender_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
) -> DuelProbabilityResult:
    attacker_outcomes = generate_duel_roll_outcomes(
        attacks=attacker_attacks,
        reroll_available=attacker_reroll_available,
        modifier=attacker_modifier,
    )

    defender_outcomes = generate_duel_roll_outcomes(
        attacks=defender_attacks,
        reroll_available=defender_reroll_available,
        modifier=defender_modifier,
    )

    attacker_wins = 0
    defender_wins = 0
    draws = 0

    for attacker_rolls in attacker_outcomes:
        for defender_rolls in defender_outcomes:
            attacker_highest, defender_highest = (
                resolve_duel_rolls_with_might(
                    attacker_rolls=attacker_rolls,
                    defender_rolls=defender_rolls,
                    attacker_might_available=attacker_might_available,
                    defender_might_available=defender_might_available,
                    attacker_might_strategy=attacker_might_strategy,
                    defender_might_strategy=defender_might_strategy,
                )
            )

            if attacker_highest > defender_highest:
                attacker_wins += 1
            elif defender_highest > attacker_highest:
                defender_wins += 1
            else:
                draws += 1

    total_outcomes = len(attacker_outcomes) * len(defender_outcomes)

    return DuelProbabilityResult(
        attacker_win_probability=attacker_wins / total_outcomes,
        defender_win_probability=defender_wins / total_outcomes,
        draw_probability=draws / total_outcomes,
    )

def calculate_duel_probability(
    attacker_attacks: int,
    attacker_fight: int,
    defender_attacks: int,
    defender_fight: int,
    attacker_reroll_available: bool = False,
    defender_reroll_available: bool = False,
    attacker_might_available: int = 0,
    defender_might_available: int = 0,
    attacker_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    defender_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
) -> DuelProbabilityResult:
    """
    Calculates Duel probabilities after resolving equal
    highest rolls using Fight value.

    If both sides have equal Fight value, tied highest rolls
    remain recorded as draws for now.
    """

    raw_result = calculate_raw_duel_probability(
        attacker_attacks=attacker_attacks,
        defender_attacks=defender_attacks,
        attacker_reroll_available=attacker_reroll_available,
        defender_reroll_available=defender_reroll_available,
        attacker_might_available=attacker_might_available,
        defender_might_available=defender_might_available,
        attacker_might_strategy=attacker_might_strategy,
        defender_might_strategy=defender_might_strategy,
        attacker_modifier=attacker_modifier,
        defender_modifier=defender_modifier,
    )

    attacker_win_probability = (
        raw_result.attacker_win_probability
    )

    defender_win_probability = (
        raw_result.defender_win_probability
    )

    draw_probability = raw_result.draw_probability

    if attacker_fight > defender_fight:
        attacker_win_probability += draw_probability
        draw_probability = 0.0

    elif defender_fight > attacker_fight:
        defender_win_probability += draw_probability
        draw_probability = 0.0

    return DuelProbabilityResult(
        attacker_win_probability=attacker_win_probability,
        defender_win_probability=defender_win_probability,
        draw_probability=draw_probability,
    )

def resolve_draw_probability_by_roll_off(
    result: DuelProbabilityResult,
    attacker_roll_off_probability: float = 0.5,
) -> DuelProbabilityResult:
    """
    Resolves any remaining draw probability using a roll-off.

    By default, each side has an equal chance of winning
    the roll-off.
    """

    if not 0.0 <= attacker_roll_off_probability <= 1.0:
        raise ValueError(
            "Attacker roll-off probability must be between 0 and 1."
        )

    attacker_draw_share = (
        result.draw_probability
        * attacker_roll_off_probability
    )

    defender_draw_share = (
        result.draw_probability
        * (1.0 - attacker_roll_off_probability)
    )

    return DuelProbabilityResult(
        attacker_win_probability=(
            result.attacker_win_probability
            + attacker_draw_share
        ),
        defender_win_probability=(
            result.defender_win_probability
            + defender_draw_share
        ),
        draw_probability=0.0,
    )

def calculate_basic_duel_probability(
    attacker_attacks: int,
    attacker_fight: int,
    defender_attacks: int,
    defender_fight: int,
    attacker_roll_off_probability: float = 0.5,
    attacker_reroll_available: bool = False,
    defender_reroll_available: bool = False,
    attacker_might_available: int = 0,
    defender_might_available: int = 0,
    attacker_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    defender_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    attacker_heroic_strike_active: bool = False,
    defender_heroic_strike_active: bool = False,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
) -> DuelProbabilityResult:
    """
    Calculates the complete basic Duel result.

    Resolves:
    1. Highest Duel dice.
    2. Fight value.
    3. Any remaining tie by roll-off.
    """

    unresolved_result = calculate_duel_probability_with_heroic_strike(
        attacker_attacks=attacker_attacks,
        attacker_fight=attacker_fight,
        defender_attacks=defender_attacks,
        defender_fight=defender_fight,
        attacker_heroic_strike_active=attacker_heroic_strike_active,
        defender_heroic_strike_active=defender_heroic_strike_active,
        attacker_reroll_available=attacker_reroll_available,
        defender_reroll_available=defender_reroll_available,
        attacker_might_available=attacker_might_available,
        defender_might_available=defender_might_available,
        attacker_might_strategy=attacker_might_strategy,
        defender_might_strategy=defender_might_strategy,
        attacker_modifier=attacker_modifier,
        defender_modifier=defender_modifier,
    )

    return resolve_draw_probability_by_roll_off(
        unresolved_result,
        attacker_roll_off_probability=attacker_roll_off_probability,
    )

def calculate_profile_duel_probability(
    attacker: Profile,
    defender: Profile,
    attacker_roll_off_probability: float = 0.5,
    attacker_reroll_available: bool = False,
    defender_reroll_available: bool = False,
    attacker_might_available: int = 0,
    defender_might_available: int = 0,
    attacker_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    defender_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    attacker_heroic_strike_active: bool = False,
    defender_heroic_strike_active: bool = False,
) -> DuelProbabilityResult:
    """
    Calculates a complete basic Duel result using two Profiles.
    """

    return calculate_basic_duel_probability(
        attacker_attacks=attacker.attacks,
        attacker_fight=attacker.fight,
        defender_attacks=defender.attacks,
        defender_fight=defender.fight,
        attacker_roll_off_probability=attacker_roll_off_probability,
        attacker_reroll_available=attacker_reroll_available,
        defender_reroll_available=defender_reroll_available,
        attacker_might_available=attacker_might_available,
        defender_might_available=defender_might_available,
        attacker_might_strategy=attacker_might_strategy,
        defender_might_strategy=defender_might_strategy,
        attacker_heroic_strike_active=attacker_heroic_strike_active,
        defender_heroic_strike_active=defender_heroic_strike_active,
)

def generate_combat_side_fight_outcomes(
    attacker_side: CombatSide,
    defender_side: CombatSide,
) -> tuple[tuple[int, int], ...]:
    """
    Generates the final highest Fight values for two combat sides,
    including participant-specific Heroic Strike outcomes.
    """

    attacker_strike_user = attacker_side.heroic_strike_user
    defender_strike_user = defender_side.heroic_strike_user

    attacker_strike_base_fight = (
        attacker_strike_user.profile.fight
        if attacker_strike_user is not None
        else attacker_side.highest_fight
    )

    defender_strike_base_fight = (
        defender_strike_user.profile.fight
        if defender_strike_user is not None
        else defender_side.highest_fight
    )

    strike_outcomes = generate_duel_fight_outcomes(
        attacker_base_fight=attacker_strike_base_fight,
        defender_base_fight=defender_strike_base_fight,
        attacker_heroic_strike_active=(
            attacker_strike_user is not None
        ),
        defender_heroic_strike_active=(
            defender_strike_user is not None
        ),
    )

    attacker_other_fight = max(
        (
            participant.profile.fight
            for participant in attacker_side.participants
            if (
                participant.contributes_fight
                and participant is not attacker_strike_user
            )
        ),
        default=0,
    )

    defender_other_fight = max(
        (
            participant.profile.fight
            for participant in defender_side.participants
            if (
                participant.contributes_fight
                and participant is not defender_strike_user
            )
        ),
        default=0,
    )

    return tuple(
        (
            max(attacker_other_fight, attacker_strike_fight),
            max(defender_other_fight, defender_strike_fight),
        )
        for attacker_strike_fight, defender_strike_fight
        in strike_outcomes
    )

def calculate_combat_side_duel_probability(
    attacker_side: CombatSide,
    defender_side: CombatSide,
    attacker_roll_off_probability: float = 0.5,
) -> DuelProbabilityResult:
    """
    Calculates a complete Duel result between two multi-model
    combat sides.
    """

    fight_outcomes = generate_combat_side_fight_outcomes(
        attacker_side=attacker_side,
        defender_side=defender_side,
    )

    attacker_probability = 0.0
    defender_probability = 0.0
    draw_probability = 0.0

    for attacker_fight, defender_fight in fight_outcomes:
        result = calculate_duel_probability(
            attacker_attacks=attacker_side.total_duel_dice,
            attacker_fight=attacker_fight,
            defender_attacks=defender_side.total_duel_dice,
            defender_fight=defender_fight,
            attacker_reroll_available=attacker_side.reroll_available,
            defender_reroll_available=defender_side.reroll_available,
            attacker_might_available=attacker_side.might_available,
            defender_might_available=defender_side.might_available,
            attacker_might_strategy=attacker_side.might_strategy,
            defender_might_strategy=defender_side.might_strategy,
        )

        attacker_probability += result.attacker_win_probability
        defender_probability += result.defender_win_probability
        draw_probability += result.draw_probability

    outcome_count = len(fight_outcomes)

    unresolved_result = DuelProbabilityResult(
        attacker_win_probability=(
            attacker_probability / outcome_count
        ),
        defender_win_probability=(
            defender_probability / outcome_count
        ),
        draw_probability=draw_probability / outcome_count,
    )

    return resolve_draw_probability_by_roll_off(
        unresolved_result,
        attacker_roll_off_probability=attacker_roll_off_probability,
    )

def apply_standard_duel_reroll(
    rolls: tuple[int, ...],
    replacement_roll: int,
) -> tuple[int, ...]:
    """
    Replaces the lowest Duel die with one new D6 result.
    """

    if not rolls:
        raise ValueError("At least one Duel die is required.")

    if not 1 <= replacement_roll <= 6:
        raise ValueError("Replacement Duel roll must be between 1 and 6.")

    lowest_index = rolls.index(min(rolls))
    updated_rolls = list(rolls)
    updated_rolls[lowest_index] = replacement_roll

    return tuple(updated_rolls)

def generate_standard_reroll_outcomes(
    rolls: tuple[int, ...],
) -> tuple[tuple[int, ...], ...]:
    """
    Generates the six equally weighted outcomes produced by
    one optional standard Duel reroll.

    The lowest die is rerolled unless the current Duel roll
    already contains a 6. When the reroll is not used, the
    original outcome is repeated six times to preserve its
    probability weight.
    """

    if not rolls:
        raise ValueError("At least one Duel die is required.")

    if max(rolls) == 6:
        return tuple(rolls for _ in range(6))

    return tuple(
        apply_standard_duel_reroll(
            rolls=rolls,
            replacement_roll=replacement_roll,
        )
        for replacement_roll in range(1, 7)
    )

def generate_duel_roll_outcomes(
    attacks: int,
    reroll_available: bool = False,
    modifier: DuelModifier | None = None,
) -> tuple[tuple[int, ...], ...]:
    """
    Generates every possible final Duel roll outcome.

    When a standard reroll is available, the lowest die
    is rerolled once and all six replacement results are included.
    """

    if attacks < 1:
        raise ValueError("A model must roll at least one Duel die.")

    initial_outcomes = tuple(
        tuple(rolls)
        for rolls in product(range(1, 7), repeat=attacks)
    )

    if not reroll_available:
        final_outcomes = initial_outcomes
    else:
        final_outcomes = tuple(
            rerolled_outcome
            for rolls in initial_outcomes
            for rerolled_outcome in generate_standard_reroll_outcomes(
                rolls
            )
        )

    if modifier is None:
        return final_outcomes

    return tuple(
        apply_duel_modifier_to_rolls(
            rolls=rolls,
            modifier=modifier,
        )
        for rolls in final_outcomes
    )

def resolve_duel_rolls_with_might(
    attacker_rolls: tuple[int, ...],
    defender_rolls: tuple[int, ...],
    attacker_might_available: int = 0,
    defender_might_available: int = 0,
    attacker_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    defender_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
) -> tuple[int, int]:
    """
    Returns each side's final highest Duel roll after Might is resolved.
    """

    if not attacker_rolls:
        raise ValueError("Attacker must have at least one Duel roll.")

    if not defender_rolls:
        raise ValueError("Defender must have at least one Duel roll.")

    resolution = resolve_duel_might(
        attacker_roll=max(attacker_rolls),
        attacker_might_available=attacker_might_available,
        attacker_strategy=attacker_might_strategy,
        defender_roll=max(defender_rolls),
        defender_might_available=defender_might_available,
        defender_strategy=defender_might_strategy,
    )

    return (
        resolution.attacker_final_roll,
        resolution.defender_final_roll,
    )

def calculate_duel_probability_with_heroic_strike(
    attacker_attacks: int,
    attacker_fight: int,
    defender_attacks: int,
    defender_fight: int,
    attacker_heroic_strike_active: bool = False,
    defender_heroic_strike_active: bool = False,
    attacker_reroll_available: bool = False,
    defender_reroll_available: bool = False,
    attacker_might_available: int = 0,
    defender_might_available: int = 0,
    attacker_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    defender_might_strategy: DuelMightStrategy = DuelMightStrategy.NEVER,
    attacker_modifier: DuelModifier | None = None,
    defender_modifier: DuelModifier | None = None,
) -> DuelProbabilityResult:
    """
    Calculates an unresolved Duel result across all possible
    Heroic Strike Fight outcomes.
    """

    fight_outcomes = generate_duel_fight_outcomes(
        attacker_base_fight=attacker_fight,
        defender_base_fight=defender_fight,
        attacker_heroic_strike_active=attacker_heroic_strike_active,
        defender_heroic_strike_active=defender_heroic_strike_active,
    )

    attacker_probability = 0.0
    defender_probability = 0.0
    draw_probability = 0.0

    for attacker_final_fight, defender_final_fight in fight_outcomes:
        result = calculate_duel_probability(
            attacker_attacks=attacker_attacks,
            attacker_fight=attacker_final_fight,
            defender_attacks=defender_attacks,
            defender_fight=defender_final_fight,
            attacker_reroll_available=attacker_reroll_available,
            defender_reroll_available=defender_reroll_available,
            attacker_might_available=attacker_might_available,
            defender_might_available=defender_might_available,
            attacker_might_strategy=attacker_might_strategy,
            defender_might_strategy=defender_might_strategy,
            attacker_modifier=attacker_modifier,
            defender_modifier=defender_modifier,
        )

        attacker_probability += result.attacker_win_probability
        defender_probability += result.defender_win_probability
        draw_probability += result.draw_probability

    outcome_count = len(fight_outcomes)

    return DuelProbabilityResult(
        attacker_win_probability=attacker_probability / outcome_count,
        defender_win_probability=defender_probability / outcome_count,
        draw_probability=draw_probability / outcome_count,
    )