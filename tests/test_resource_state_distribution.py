import pytest

from hero_resource_state import HeroResourceState
from resistance_resource_state_probability import (
    WeightedHeroResourceState,
    resistance_resource_state_distribution,
)
from resource_state_distribution import (
    combine_weighted_resource_states,
    propagate_resource_distribution,
)


def test_combine_weighted_resource_states_merges_duplicates():
    state = HeroResourceState(
        remaining_will=2,
    )

    outcomes = (
        WeightedHeroResourceState(
            state=state,
            probability=0.25,
        ),
        WeightedHeroResourceState(
            state=state,
            probability=0.75,
        ),
    )

    combined = combine_weighted_resource_states(
        outcomes
    )

    assert len(combined) == 1
    assert combined[0].state == state
    assert combined[0].probability == pytest.approx(
        1.0
    )


def test_propagate_resource_distribution_across_two_resists():
    initial = (
        WeightedHeroResourceState(
            state=HeroResourceState(
                remaining_will=2,
            ),
            probability=1.0,
        ),
    )

    def resist_once(state):
        return resistance_resource_state_distribution(
            resources=state,
            paid_dice_count=1,
            starting_will=2,
        )

    after_first = propagate_resource_distribution(
        outcomes=initial,
        transition=resist_once,
    )

    after_second = propagate_resource_distribution(
        outcomes=after_first,
        transition=resist_once,
    )

    assert sum(
        outcome.probability
        for outcome in after_second
    ) == pytest.approx(1.0)

def test_two_resists_produce_expected_will_distribution():
    initial = (
        WeightedHeroResourceState(
            state=HeroResourceState(
                remaining_will=2,
            ),
            probability=1.0,
        ),
    )

    def resist_once(state):
        return resistance_resource_state_distribution(
            resources=state,
            paid_dice_count=1,
            starting_will=2,
        )

    after_first = propagate_resource_distribution(
        outcomes=initial,
        transition=resist_once,
    )

    after_second = propagate_resource_distribution(
        outcomes=after_first,
        transition=resist_once,
    )

    probabilities_by_will = {
        outcome.state.remaining_will:
        outcome.probability
        for outcome in after_second
    }

    assert probabilities_by_will[0] == pytest.approx(
        25 / 36
    )
    assert probabilities_by_will[1] == pytest.approx(
        10 / 36
    )
    assert probabilities_by_will[2] == pytest.approx(
        1 / 36
    )