"""
Project Palantír
================

Spell casting probability calculations.

DEV-025.2 – Spell Reliability
"""
from hero_resource_state import HeroResourceState
from profile_spell_assignment import ProfileSpellAssignment

def casting_probability(
    cast_value: int,
    dice_count: int = 1,
) -> float:
    """
    Returns the probability of successfully casting
    a spell using one or more D6.
    """

    single_die_failure_probability = (
        cast_value - 1
    ) / 6

    all_dice_fail_probability = (
        single_die_failure_probability
        ** dice_count
    )

    return 1 - all_dice_fail_probability

def casting_probability_with_resource_state(
    cast_value: int,
    resources: HeroResourceState,
    will_points_to_spend: int,
) -> float:
    if will_points_to_spend < 1:
        raise ValueError(
            "At least one Will Point must be spent to cast."
        )

    if will_points_to_spend > resources.remaining_will:
        raise ValueError(
            "Cannot spend more Will than the caster has remaining."
        )

    return casting_probability(
        cast_value=cast_value,
        dice_count=will_points_to_spend,
    )

def casting_probability_for_spell_assignment(
    spell_assignment: ProfileSpellAssignment,
    dice_count: int = 1,
) -> float:
    return casting_probability(
        cast_value=spell_assignment.cast_value,
        dice_count=dice_count,
    )

def heroic_channelling_cast_probability(
    resources: HeroResourceState,
) -> float:
    if resources.remaining_will < 1:
        raise ValueError(
            "Heroic Channelling still requires one Will Point to cast."
        )

    return 1.0

def heroic_channelling_cast_result(
    resources: HeroResourceState,
) -> int:
    if resources.remaining_will < 1:
        raise ValueError(
            "Heroic Channelling still requires one Will Point to cast."
        )

    return 6