import pytest

from hero_resource_spending import spend_will
from hero_resource_state import HeroResourceState
from magical_power_resolution_probability import (
    magical_power_effect_probability_with_resource_state,
)


def test_spellcasting_resource_regression():
    caster_resources = HeroResourceState(
        remaining_will=3,
    )

    defender_resources = HeroResourceState(
        remaining_will=2,
    )

    probability = (
        magical_power_effect_probability_with_resource_state(
            cast_value=4,
            caster_resources=caster_resources,
            casting_will_to_spend=2,
            defender_resources=defender_resources,
            resistance_will_to_spend=1,
        )
    )

    assert probability == pytest.approx(
        14 / 27
    )

    caster_after_cast = spend_will(
        caster_resources,
        amount=2,
    )

    defender_after_resist = spend_will(
        defender_resources,
        amount=1,
    )

    assert caster_after_cast.remaining_will == 1
    assert defender_after_resist.remaining_will == 1