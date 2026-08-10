from fractions import Fraction

from wound_target import WoundTarget
from math import comb

from profiles import Profile
from wound_table import get_wound_target
from wound_modifier import WoundModifier
from wound_reroll import WoundReroll

def get_wound_probability(
    target: WoundTarget | None,
) -> Fraction:
    if target is None:
        return Fraction(0, 1)

    first_roll_probability = Fraction(
        7 - target.first_roll,
        6,
    )

    if target.second_roll is None:
        return first_roll_probability

    second_roll_probability = Fraction(
        7 - target.second_roll,
        6,
    )

    return (
        first_roll_probability
        * second_roll_probability
    )

def get_roll_probability_with_reroll(
    required_roll: int,
    reroll: WoundReroll,
) -> Fraction:
    if required_roll <= 1:
        base_probability = Fraction(1, 1)
    elif required_roll > 6:
        base_probability = Fraction(0, 1)
    else:
        base_probability = Fraction(
            7 - required_roll,
            6,
        )

    if reroll.reroll_failed:
        return (
            base_probability
            + (Fraction(1, 1) - base_probability)
            * base_probability
        )

    if reroll.reroll_natural_ones:
        natural_one_success = (
            Fraction(1, 1)
            if required_roll <= 1
            else Fraction(0, 1)
        )

        return (
            base_probability
            - Fraction(1, 6)
            * natural_one_success
            + Fraction(1, 6)
            * base_probability
        )

    return base_probability

def get_wound_distribution(
    number_of_strikes: int,
    wound_probability: Fraction,
) -> tuple[Fraction, ...]:
    if number_of_strikes < 0:
        raise ValueError(
            "number_of_strikes must not be negative"
        )

    if not Fraction(0, 1) <= wound_probability <= Fraction(1, 1):
        raise ValueError(
            "wound_probability must be between 0 and 1"
        )

    miss_probability = Fraction(1, 1) - wound_probability

    return tuple(
        Fraction(comb(number_of_strikes, wounds), 1)
        * wound_probability**wounds
        * miss_probability**(number_of_strikes - wounds)
        for wounds in range(number_of_strikes + 1)
    )

def get_expected_wounds(
    number_of_strikes: int,
    wound_probability: Fraction,
) -> Fraction:
    if number_of_strikes < 0:
        raise ValueError(
            "number_of_strikes must not be negative"
        )

    if not Fraction(0, 1) <= wound_probability <= Fraction(1, 1):
        raise ValueError(
            "wound_probability must be between 0 and 1"
        )

    return number_of_strikes * wound_probability

def get_profile_wound_probability(
    attacker: Profile,
    defender: Profile,
) -> Fraction:
    target = get_wound_target(
        strength=attacker.strength,
        defence=defender.defence,
    )

    return get_wound_probability(target)

def get_modified_wound_probability(
    target: WoundTarget | None,
    modifier: WoundModifier,
) -> Fraction:
    if target is None:
        return Fraction(0, 1)

    def roll_probability(
        required_roll: int,
    ) -> Fraction:
        effective_required_roll = (
            required_roll - modifier.to_wound
        )

        if effective_required_roll <= 1:
            return Fraction(1, 1)

        if effective_required_roll > 6:
            return Fraction(0, 1)

        return Fraction(
            7 - effective_required_roll,
            6,
        )

    first_roll_probability = roll_probability(
        target.first_roll,
    )

    if target.second_roll is None:
        return first_roll_probability

    second_roll_probability = roll_probability(
        target.second_roll,
    )

    return (
        first_roll_probability
        * second_roll_probability
    )

def get_wound_probability_with_reroll(
    target: WoundTarget | None,
    reroll: WoundReroll,
) -> Fraction:
    if target is None:
        return Fraction(0, 1)

    first_roll_probability = (
        get_roll_probability_with_reroll(
            required_roll=target.first_roll,
            reroll=reroll,
        )
    )

    if target.second_roll is None:
        return first_roll_probability

    second_roll_probability = (
        get_roll_probability_with_reroll(
            required_roll=target.second_roll,
            reroll=reroll,
        )
    )

    return (
        first_roll_probability
        * second_roll_probability
    )

def get_modified_wound_probability_with_reroll(
    target: WoundTarget | None,
    modifier: WoundModifier,
    reroll: WoundReroll,
) -> Fraction:
    if target is None:
        return Fraction(0, 1)

    def roll_probability(
        required_roll: int,
    ) -> Fraction:
        effective_required_roll = (
            required_roll - modifier.to_wound
        )

        return get_roll_probability_with_reroll(
            required_roll=effective_required_roll,
            reroll=reroll,
        )

    first_roll_probability = roll_probability(
        target.first_roll,
    )

    if target.second_roll is None:
        return first_roll_probability

    second_roll_probability = roll_probability(
        target.second_roll,
    )

    return (
        first_roll_probability
        * second_roll_probability
    )