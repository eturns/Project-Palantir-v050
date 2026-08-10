from dataclasses import dataclass

from battle_length_assumption import BattleLengthAssumption
from hero_resource_state import HeroResourceState
from resource_strategy import ResourceStrategy
from resource_strategy_budget import (
    calculate_turn_resource_budget,
)

@dataclass(frozen=True)
class ResourceStrategyResult:
    strategy: ResourceStrategy
    battle_length: BattleLengthAssumption
    turn_resources: tuple[HeroResourceState, ...]
    final_resources: HeroResourceState

def compare_resource_strategies(
    initial_resources: HeroResourceState,
    battle_length: BattleLengthAssumption,
) -> tuple[ResourceStrategyResult, ...]:
    results = []

    for strategy in ResourceStrategy:
        resources = initial_resources
        turn_resources = []

        for turn_number in range(
            1,
            battle_length.assumed_turns + 1,
        ):
            turns_remaining = (
                battle_length.assumed_turns
                - turn_number
                + 1
            )

            budget = calculate_turn_resource_budget(
                resources=resources,
                turns_remaining=turns_remaining,
                strategy=strategy,
            )

            resources = HeroResourceState(
                remaining_might=(
                    resources.remaining_might
                    - budget.remaining_might
                ),
                remaining_will=(
                    resources.remaining_will
                    - budget.remaining_will
                ),
                remaining_fate=(
                    resources.remaining_fate
                    - budget.remaining_fate
                ),
            )

            turn_resources.append(resources)

        results.append(
            ResourceStrategyResult(
                strategy=strategy,
                battle_length=battle_length,
                turn_resources=tuple(turn_resources),
                final_resources=resources,
            )
        )

    return tuple(results)