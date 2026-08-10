from itertools import product
from hero_resource_state import HeroResourceState

def magical_power_effect_probability(
    cast_value: int,
    casting_dice_count: int,
    resistance_dice_count: int,
) -> float:
    if casting_dice_count < 1:
        raise ValueError(
            "Casting dice count must be at least one."
        )

    if resistance_dice_count < 0:
        raise ValueError(
            "Resistance dice count cannot be negative."
        )

    successful_effect_outcomes = 0
    total_outcomes = 0

    casting_outcomes = product(
        range(1, 7),
        repeat=casting_dice_count,
    )

    for casting_rolls in casting_outcomes:
        highest_casting_roll = max(casting_rolls)

        if resistance_dice_count == 0:
            total_outcomes += 1

            if highest_casting_roll >= cast_value:
                successful_effect_outcomes += 1

            continue

        resistance_outcomes = product(
            range(1, 7),
            repeat=resistance_dice_count,
        )

        for resistance_rolls in resistance_outcomes:
            total_outcomes += 1

            if highest_casting_roll < cast_value:
                continue

            highest_resistance_roll = max(
                resistance_rolls
            )

            if (
                highest_resistance_roll
                < highest_casting_roll
            ):
                successful_effect_outcomes += 1

    return (
        successful_effect_outcomes
        / total_outcomes
    )

def magical_power_effect_probability_with_resource_state(
    cast_value: int,
    caster_resources: HeroResourceState,
    casting_will_to_spend: int,
    defender_resources: HeroResourceState,
    resistance_will_to_spend: int,
) -> float:
    if casting_will_to_spend < 1:
        raise ValueError(
            "At least one Will Point must be spent to cast."
        )

    if casting_will_to_spend > caster_resources.remaining_will:
        raise ValueError(
            "Cannot spend more Will than the caster has remaining."
        )

    if resistance_will_to_spend < 0:
        raise ValueError(
            "Resistance Will spend cannot be negative."
        )

    if resistance_will_to_spend > defender_resources.remaining_will:
        raise ValueError(
            "Cannot spend more Will than the defender has remaining."
        )

    return magical_power_effect_probability(
        cast_value=cast_value,
        casting_dice_count=casting_will_to_spend,
        resistance_dice_count=resistance_will_to_spend,
    )