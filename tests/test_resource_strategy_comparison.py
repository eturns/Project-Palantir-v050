from battle_length_assumption import (
    BattleEndType,
    BattleLengthAssumption,
)
from hero_resource_state import HeroResourceState
from resource_strategy import ResourceStrategy
from resource_strategy_comparison import (
    ResourceStrategyResult,
    compare_resource_strategies,
)


def test_resource_strategy_result_stores_reproducible_inputs():
    result = ResourceStrategyResult(
        strategy=ResourceStrategy.BALANCED,
        battle_length=BattleLengthAssumption(
            assumed_turns=8,
            end_type=BattleEndType.BROKEN_RANDOM_END,
        ),
        turn_resources=(
            HeroResourceState(
                remaining_might=2,
                remaining_will=4,
                remaining_fate=1,
            ),
            HeroResourceState(
                remaining_might=1,
                remaining_will=2,
                remaining_fate=1,
            ),
        ),
        final_resources=HeroResourceState(
            remaining_might=1,
            remaining_will=2,
            remaining_fate=1,
        ),
    )

    assert result.strategy == ResourceStrategy.BALANCED
    assert result.battle_length.assumed_turns == 8
    assert result.final_resources == HeroResourceState(
        remaining_might=1,
        remaining_will=2,
        remaining_fate=1,
    )

def test_compare_resource_strategies_returns_all_strategies():
    results = compare_resource_strategies(
        initial_resources=HeroResourceState(
            remaining_might=3,
            remaining_will=5,
            remaining_fate=2,
        ),
        battle_length=BattleLengthAssumption(
            assumed_turns=3,
            end_type=BattleEndType.FIXED_TURNS,
        ),
    )

    assert tuple(
        result.strategy
        for result in results
    ) == (
        ResourceStrategy.CONSERVATIVE,
        ResourceStrategy.BALANCED,
        ResourceStrategy.AGGRESSIVE,
    )


def test_resource_strategy_comparison_is_reproducible():
    initial_resources = HeroResourceState(
        remaining_might=3,
        remaining_will=5,
        remaining_fate=2,
    )

    battle_length = BattleLengthAssumption(
        assumed_turns=3,
        end_type=BattleEndType.FIXED_TURNS,
    )

    first = compare_resource_strategies(
        initial_resources=initial_resources,
        battle_length=battle_length,
    )

    second = compare_resource_strategies(
        initial_resources=initial_resources,
        battle_length=battle_length,
    )

    assert first == second

def test_strategies_produce_different_resource_trajectories():
    results = compare_resource_strategies(
        initial_resources=HeroResourceState(
            remaining_might=3,
            remaining_will=5,
            remaining_fate=2,
        ),
        battle_length=BattleLengthAssumption(
            assumed_turns=3,
            end_type=BattleEndType.FIXED_TURNS,
        ),
    )

    results_by_strategy = {
        result.strategy: result
        for result in results
    }

    conservative = results_by_strategy[
        ResourceStrategy.CONSERVATIVE
    ]
    aggressive = results_by_strategy[
        ResourceStrategy.AGGRESSIVE
    ]

    assert (
        conservative.turn_resources[0].remaining_will
        > aggressive.turn_resources[0].remaining_will
    )

    assert (
        conservative.turn_resources[0].remaining_might
        > aggressive.turn_resources[0].remaining_might
    )