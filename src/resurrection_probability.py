from fractions import Fraction
from hero_resource_state import HeroResourceState

from master_of_the_nazgul import (
    get_master_of_the_nazgul_resurrection_modifier,
)
UNHOLY_RESURRECTION_TARGET = 3


def get_resurrection_success_probability(
    required_roll: int = UNHOLY_RESURRECTION_TARGET,
    roll_modifier: int = 0,
) -> Fraction:
    successful_rolls = 0

    for natural_roll in range(1, 7):
        modified_roll = natural_roll + roll_modifier

        if modified_roll >= required_roll:
            successful_rolls += 1

    return Fraction(
        successful_rolls,
        6,
    )

def get_resurrection_probability_with_master_of_the_nazgul(
    necromancer_remaining_will: int,
    distance_inches: float,
    required_roll: int = UNHOLY_RESURRECTION_TARGET,
    additional_roll_modifier: int = 0,
) -> Fraction:
    master_modifier = (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=necromancer_remaining_will,
            distance_inches=distance_inches,
        )
    )

    return get_resurrection_success_probability(
        required_roll=required_roll,
        roll_modifier=(
            master_modifier
            + additional_roll_modifier
        ),
    )

def get_resurrection_probability_with_necromancer_will(
    necromancer_remaining_will: int,
    distance_inches: float,
    will_points_available_to_spend: int,
    required_roll: int = UNHOLY_RESURRECTION_TARGET,
    additional_roll_modifier: int = 0,
) -> Fraction:
    if will_points_available_to_spend < 0:
        raise ValueError(
            "Will points available to spend cannot be negative."
        )

    if will_points_available_to_spend > necromancer_remaining_will:
        raise ValueError(
            "Cannot spend more Will than the Necromancer has remaining."
        )

    master_modifier = (
        get_master_of_the_nazgul_resurrection_modifier(
            remaining_will=necromancer_remaining_will,
            distance_inches=distance_inches,
        )
    )

    if master_modifier == 0:
        will_points_available_to_spend = 0

    successful_rolls = 0

    for natural_roll in range(1, 7):
        modified_roll = (
            natural_roll
            + master_modifier
            + additional_roll_modifier
        )

        will_required = max(
            0,
            required_roll - modified_roll,
        )

        if will_required <= will_points_available_to_spend:
            successful_rolls += 1

    return Fraction(
        successful_rolls,
        6,
    )

def get_resurrection_probability_with_resource_state(
    necromancer_resources: HeroResourceState,
    distance_inches: float,
    will_points_available_to_spend: int,
    required_roll: int = UNHOLY_RESURRECTION_TARGET,
    additional_roll_modifier: int = 0,
) -> Fraction:
    return get_resurrection_probability_with_necromancer_will(
        necromancer_remaining_will=(
            necromancer_resources.remaining_will
        ),
        distance_inches=distance_inches,
        will_points_available_to_spend=(
            will_points_available_to_spend
        ),
        required_roll=required_roll,
        additional_roll_modifier=additional_roll_modifier,
    )