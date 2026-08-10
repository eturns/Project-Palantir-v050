import pytest
from hero_resource_state import HeroResourceState
from magical_power_resolution_probability import (
    magical_power_effect_probability,
    magical_power_effect_probability_with_resource_state,
)


def test_unresisted_three_plus_cast_on_one_die():
    assert magical_power_effect_probability(
        cast_value=3,
        casting_dice_count=1,
        resistance_dice_count=0,
    ) == pytest.approx(
        2 / 3
    )


def test_one_die_cast_and_one_die_resist():
    assert magical_power_effect_probability(
        cast_value=3,
        casting_dice_count=1,
        resistance_dice_count=1,
    ) == pytest.approx(
        7 / 18
    )


def test_more_casting_dice_improve_effect_probability():
    one_die = magical_power_effect_probability(
        cast_value=3,
        casting_dice_count=1,
        resistance_dice_count=1,
    )

    two_dice = magical_power_effect_probability(
        cast_value=3,
        casting_dice_count=2,
        resistance_dice_count=1,
    )

    assert two_dice > one_die


def test_more_resistance_dice_reduce_effect_probability():
    one_resist_die = magical_power_effect_probability(
        cast_value=3,
        casting_dice_count=2,
        resistance_dice_count=1,
    )

    two_resist_dice = magical_power_effect_probability(
        cast_value=3,
        casting_dice_count=2,
        resistance_dice_count=2,
    )

    assert two_resist_dice < one_resist_die

def test_resource_state_magic_resolution_uses_both_will_pools():
    caster_resources = HeroResourceState(
        remaining_will=2,
    )

    defender_resources = HeroResourceState(
        remaining_will=1,
    )

    result = magical_power_effect_probability_with_resource_state(
        cast_value=3,
        caster_resources=caster_resources,
        casting_will_to_spend=2,
        defender_resources=defender_resources,
        resistance_will_to_spend=1,
    )

    assert result == pytest.approx(
        magical_power_effect_probability(
            cast_value=3,
            casting_dice_count=2,
            resistance_dice_count=1,
        )
    )


def test_resource_state_magic_resolution_rejects_caster_overspend():
    with pytest.raises(
        ValueError,
        match=(
            "Cannot spend more Will than the "
            "caster has remaining."
        ),
    ):
        magical_power_effect_probability_with_resource_state(
            cast_value=3,
            caster_resources=HeroResourceState(
                remaining_will=1,
            ),
            casting_will_to_spend=2,
            defender_resources=HeroResourceState(),
            resistance_will_to_spend=0,
        )


def test_resource_state_magic_resolution_rejects_defender_overspend():
    with pytest.raises(
        ValueError,
        match=(
            "Cannot spend more Will than the "
            "defender has remaining."
        ),
    ):
        magical_power_effect_probability_with_resource_state(
            cast_value=3,
            caster_resources=HeroResourceState(
                remaining_will=1,
            ),
            casting_will_to_spend=1,
            defender_resources=HeroResourceState(
                remaining_will=1,
            ),
            resistance_will_to_spend=2,
        )