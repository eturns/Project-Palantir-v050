from hero_resource_state import HeroResourceState


def resistance_probability(
    casting_highest_roll: int,
    dice_count: int = 1,
) -> float:
    if not 1 <= casting_highest_roll <= 6:
        raise ValueError(
            "Casting highest roll must be between 1 and 6."
        )

    if dice_count < 0:
        raise ValueError(
            "Resistance dice count cannot be negative."
        )

    if dice_count == 0:
        return 0.0

    single_die_failure_probability = (
        casting_highest_roll - 1
    ) / 6

    all_dice_fail_probability = (
        single_die_failure_probability
        ** dice_count
    )

    return 1 - all_dice_fail_probability


def resistance_probability_with_resource_state(
    casting_highest_roll: int,
    resources: HeroResourceState,
    will_points_to_spend: int,
) -> float:
    if will_points_to_spend < 0:
        raise ValueError(
            "Will points to spend cannot be negative."
        )

    if will_points_to_spend > resources.remaining_will:
        raise ValueError(
            "Cannot spend more Will than the defender has remaining."
        )

    return resistance_probability(
        casting_highest_roll=casting_highest_roll,
        dice_count=will_points_to_spend,
    )