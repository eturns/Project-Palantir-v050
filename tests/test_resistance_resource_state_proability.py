import pytest

from hero_resource_state import HeroResourceState
from resistance_resource_state_probability import (
    resistance_resource_state_distribution,
)


def test_one_paid_resist_die_creates_two_resource_states():
    resources = HeroResourceState(
        remaining_might=2,
        remaining_will=3,
        remaining_fate=1,
    )

    outcomes = resistance_resource_state_distribution(
        resources=resources,
        paid_dice_count=1,
        starting_will=3,
    )

    assert len(outcomes) == 2

    assert outcomes[0].state == HeroResourceState(
        remaining_might=2,
        remaining_will=2,
        remaining_fate=1,
    )
    assert outcomes[0].probability == pytest.approx(
        5 / 6
    )

    assert outcomes[1].state == HeroResourceState(
        remaining_might=2,
        remaining_will=3,
        remaining_fate=1,
    )
    assert outcomes[1].probability == pytest.approx(
        1 / 6
    )


def test_two_paid_resist_dice_create_refund_branches():
    resources = HeroResourceState(
        remaining_will=4,
    )

    outcomes = resistance_resource_state_distribution(
        resources=resources,
        paid_dice_count=2,
        starting_will=4,
    )

    assert outcomes[0].state.remaining_will == 2
    assert outcomes[0].probability == pytest.approx(
        25 / 36
    )

    assert outcomes[1].state.remaining_will == 3
    assert outcomes[1].probability == pytest.approx(
        10 / 36
    )

    assert outcomes[2].state.remaining_will == 4
    assert outcomes[2].probability == pytest.approx(
        1 / 36
    )


def test_resource_state_distribution_sums_to_one():
    resources = HeroResourceState(
        remaining_will=3,
    )

    outcomes = resistance_resource_state_distribution(
        resources=resources,
        paid_dice_count=2,
        starting_will=3,
    )

    assert sum(
        outcome.probability
        for outcome in outcomes
    ) == pytest.approx(1.0)


def test_resource_state_distribution_preserves_original_state():
    resources = HeroResourceState(
        remaining_might=1,
        remaining_will=3,
        remaining_fate=2,
    )

    resistance_resource_state_distribution(
        resources=resources,
        paid_dice_count=1,
        starting_will=3,
    )

    assert resources == HeroResourceState(
        remaining_might=1,
        remaining_will=3,
        remaining_fate=2,
    )