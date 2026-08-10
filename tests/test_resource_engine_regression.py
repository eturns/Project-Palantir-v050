import pytest

from battle_length_assumption import (
    BattleEndType,
    BattleLengthAssumption,
)
from hero_resource_state import HeroResourceState
from resistance_resource_state_probability import (
    WeightedHeroResourceState,
    resistance_resource_state_distribution,
)
from resource_allocation import (
    ResourceAllocation,
    apply_resource_allocations,
)
from resource_spend_domain import ResourceSpendDomain
from resource_state_distribution import (
    propagate_resource_distribution,
)
from resource_strategy import ResourceStrategy
from resource_strategy_budget import (
    calculate_turn_resource_budget,
)


def test_multi_turn_resource_engine_regression():
    battle_length = BattleLengthAssumption(
        assumed_turns=3,
        end_type=BattleEndType.BROKEN_RANDOM_END,
    )

    initial_resources = HeroResourceState(
        remaining_might=3,
        remaining_will=4,
        remaining_fate=1,
    )

    turn_one_budget = calculate_turn_resource_budget(
        resources=initial_resources,
        turns_remaining=battle_length.assumed_turns,
        strategy=ResourceStrategy.BALANCED,
    )

    assert turn_one_budget == HeroResourceState(
        remaining_might=1,
        remaining_will=2,
        remaining_fate=1,
    )

    after_turn_one = apply_resource_allocations(
        resources=initial_resources,
        allocations=(
            ResourceAllocation(
                domain=ResourceSpendDomain.COMBAT,
                might=1,
            ),
            ResourceAllocation(
                domain=ResourceSpendDomain.MAGIC,
                will=1,
            ),
        ),
    )

    assert after_turn_one == HeroResourceState(
        remaining_might=2,
        remaining_will=3,
        remaining_fate=1,
    )

    distribution = (
        WeightedHeroResourceState(
            state=after_turn_one,
            probability=1.0,
        ),
    )

    def resist_once(state):
        return resistance_resource_state_distribution(
            resources=state,
            paid_dice_count=1,
            starting_will=4,
        )

    after_resist = propagate_resource_distribution(
        outcomes=distribution,
        transition=resist_once,
    )

    probabilities_by_will = {
        outcome.state.remaining_will:
        outcome.probability
        for outcome in after_resist
    }

    assert probabilities_by_will[2] == pytest.approx(
        5 / 6
    )

    assert probabilities_by_will[3] == pytest.approx(
        1 / 6
    )

    assert initial_resources == HeroResourceState(
        remaining_might=3,
        remaining_will=4,
        remaining_fate=1,
    )