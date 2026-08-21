from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_pacing_score import (
    calculate_resource_pacing_score,
)
from resource_strategy_budget import (
    calculate_resource_budget,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)

def _calculate_owner_resource_trajectory(
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
        trajectory.append(remaining)

    return tuple(trajectory)


def calculate_owned_resource_endurance(
    states: tuple[
        OwnedHeroResourceState,
        ...,
    ],
    assumption: ResourceEnduranceAssumption,
    permissions: tuple[
        OwnedResourceUsePermission,
        ...,
    ] = (),
    conversions: tuple[
        OwnedResourceConversion,
        ...,
    ] = (),
) -> float:

    _ = (
        permissions,
        conversions,
    )
    
    scores: list[float] = []

    turns = assumption.horizon.value

    for state in states:
        resources = state.resources

        resource_values = (
            resources.remaining_might,
            resources.remaining_will,
            resources.remaining_fate,
        )

        for starting_resource in resource_values:
            if starting_resource <= 0:
                continue

            trajectory = _calculate_owner_resource_trajectory(
                starting_resource=starting_resource,
                turns=turns,
                strategy=assumption.strategy,
            )

            scores.append(
                calculate_resource_pacing_score(
                    starting_resource=starting_resource,
                    remaining_by_turn=trajectory,
                )
            )

    if not scores:
        return 0.0

    return sum(scores) / len(scores)