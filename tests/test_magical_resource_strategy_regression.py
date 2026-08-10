from hero_resource_state import HeroResourceState
from magical_resource_transition import (
    MagicalResourceSpend,
    apply_magical_resource_spend,
)
from spell_probability import (
    casting_probability_with_resource_state,
)


def test_multi_turn_magical_resource_regression():
    initial_state = HeroResourceState(
        remaining_might=2,
        remaining_will=4,
        remaining_fate=1,
    )

    first_cast_probability = (
        casting_probability_with_resource_state(
            cast_value=4,
            resources=initial_state,
            will_points_to_spend=2,
        )
    )

    state_after_first_cast = (
        apply_magical_resource_spend(
            initial_state,
            MagicalResourceSpend(
                will=2,
            ),
        )
    )

    second_cast_probability = (
        casting_probability_with_resource_state(
            cast_value=4,
            resources=state_after_first_cast,
            will_points_to_spend=1,
        )
    )

    final_state = apply_magical_resource_spend(
        state_after_first_cast,
        MagicalResourceSpend(
            will=1,
            might=1,
        ),
    )

    assert first_cast_probability == 0.75
    assert second_cast_probability == 0.5

    assert initial_state == HeroResourceState(
        remaining_might=2,
        remaining_will=4,
        remaining_fate=1,
    )

    assert state_after_first_cast == HeroResourceState(
        remaining_might=2,
        remaining_will=2,
        remaining_fate=1,
    )

    assert final_state == HeroResourceState(
        remaining_might=1,
        remaining_will=1,
        remaining_fate=1,
    )