from hero_resource_state import HeroResourceState
from resistance_resource_resolution import (
    resolve_resistance_resources,
)


def test_paid_resist_die_spends_will():
    state = HeroResourceState(
        remaining_will=3,
    )

    result = resolve_resistance_resources(
        state=state,
        starting_will=3,
        paid_resist_rolls=(4,),
    )

    assert result.remaining_will == 2


def test_natural_six_on_paid_resist_die_refunds_will():
    state = HeroResourceState(
        remaining_will=3,
    )

    result = resolve_resistance_resources(
        state=state,
        starting_will=3,
        paid_resist_rolls=(6,),
    )

    assert result.remaining_will == 3


def test_multiple_paid_natural_sixes_refund_each_will():
    state = HeroResourceState(
        remaining_will=3,
    )

    result = resolve_resistance_resources(
        state=state,
        starting_will=3,
        paid_resist_rolls=(6, 6),
    )

    assert result.remaining_will == 3


def test_free_resist_die_does_not_spend_will():
    state = HeroResourceState(
        remaining_will=2,
    )

    result = resolve_resistance_resources(
        state=state,
        starting_will=2,
        paid_resist_rolls=(),
        free_resist_rolls=(4,),
    )

    assert result.remaining_will == 2


def test_natural_six_on_free_resist_die_does_not_refund_will():
    state = HeroResourceState(
        remaining_will=1,
    )

    result = resolve_resistance_resources(
        state=state,
        starting_will=3,
        paid_resist_rolls=(),
        free_resist_rolls=(6,),
    )

    assert result.remaining_will == 1