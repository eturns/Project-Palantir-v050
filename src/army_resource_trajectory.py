from dataclasses import dataclass

from army_resource_state import ArmyResourceState
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_strategy_budget import (
    calculate_resource_budget,
)


@dataclass(frozen=True)
class ArmyResourceTrajectory:
    might: tuple[int, ...]
    will: tuple[int, ...]
    fate: tuple[int, ...]


def _calculate_resource_trajectory(
    starting_resource: int,
    turns: int,
    strategy,
) -> tuple[int, ...]:
    remaining = starting_resource
    trajectory = []

    for turn_number in range(
        1,
        turns + 1,
    ):
        turns_remaining = (
            turns
            - turn_number
            + 1
        )

        budget = calculate_resource_budget(
            remaining_resource=remaining,
            turns_remaining=turns_remaining,
            strategy=strategy,
        )

        remaining -= budget

        trajectory.append(
            remaining,
        )

    return tuple(
        trajectory,
    )


def calculate_army_resource_trajectory(
    resources: ArmyResourceState,
    assumption: ResourceEnduranceAssumption,
) -> ArmyResourceTrajectory:
    turns = assumption.horizon.value

    return ArmyResourceTrajectory(
        might=_calculate_resource_trajectory(
            starting_resource=resources.might,
            turns=turns,
            strategy=assumption.strategy,
        ),
        will=_calculate_resource_trajectory(
            starting_resource=resources.will,
            turns=turns,
            strategy=assumption.strategy,
        ),
        fate=_calculate_resource_trajectory(
            starting_resource=resources.fate,
            turns=turns,
            strategy=assumption.strategy,
        ),
    )