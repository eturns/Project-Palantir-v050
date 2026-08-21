from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_totals import (
    calculate_owned_resource_allocation_totals,
)
from resource_strategy import ResourceStrategy
from resource_strategy_budget import (
    calculate_turn_resource_budget,
)
from resource_use_permission import ResourceType


def owned_strategy_allows_allocations(
    states: tuple[
        OwnedHeroResourceState,
        ...,
    ],
    turns_remaining: int,
    strategy: ResourceStrategy,
    allocations: tuple[
        OwnedResourceAllocation,
        ...,
    ],
) -> bool:
    states_by_owner = {
        state.owner: state
        for state in states
    }

    for allocation in allocations:
        if allocation.owner not in states_by_owner:
            return False

    totals = calculate_owned_resource_allocation_totals(
        allocations,
    )

    for state in states:
        budget = calculate_turn_resource_budget(
            resources=state.resources,
            turns_remaining=turns_remaining,
            strategy=strategy,
        )

        might_spend = totals.get(
            (
                state.owner,
                ResourceType.MIGHT,
            ),
            0,
        )

        will_spend = totals.get(
            (
                state.owner,
                ResourceType.WILL,
            ),
            0,
        )

        fate_spend = totals.get(
            (
                state.owner,
                ResourceType.FATE,
            ),
            0,
        )

        if might_spend > budget.remaining_might:
            return False

        if will_spend > budget.remaining_will:
            return False

        if fate_spend > budget.remaining_fate:
            return False

    return True