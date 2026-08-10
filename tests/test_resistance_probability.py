import pytest

from hero_resource_state import HeroResourceState
from resistance_probability import (
    resistance_probability,
    resistance_probability_with_resource_state,
)


def test_single_die_resists_casting_roll_of_four_half_the_time():
    assert resistance_probability(
        casting_highest_roll=4,
    ) == pytest.approx(
        1 / 2
    )


def test_two_resist_dice_improve_probability():
    assert resistance_probability(
        casting_highest_roll=4,
        dice_count=2,
    ) == pytest.approx(
        3 / 4
    )


def test_zero_resist_dice_cannot_resist():
    assert resistance_probability(
        casting_highest_roll=4,
        dice_count=0,
    ) == 0


def test_resistance_uses_available_will():
    resources = HeroResourceState(
        remaining_will=2,
    )

    assert resistance_probability_with_resource_state(
        casting_highest_roll=4,
        resources=resources,
        will_points_to_spend=2,
    ) == pytest.approx(
        3 / 4
    )


def test_resistance_rejects_overspend():
    resources = HeroResourceState(
        remaining_will=1,
    )

    with pytest.raises(
        ValueError,
        match=(
            "Cannot spend more Will than the "
            "defender has remaining."
        ),
    ):
        resistance_probability_with_resource_state(
            casting_highest_roll=4,
            resources=resources,
            will_points_to_spend=2,
        )