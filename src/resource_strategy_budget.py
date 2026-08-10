from math import ceil

from hero_resource_state import HeroResourceState
from resource_strategy import ResourceStrategy
from resource_allocation import ResourceAllocation

def calculate_resource_budget(
    remaining_resource: int,
    turns_remaining: int,
    strategy: ResourceStrategy,
) -> int:
    if remaining_resource < 0:
        raise ValueError(
            "Remaining resource cannot be negative."
        )

    if turns_remaining < 1:
        raise ValueError(
            "Turns remaining must be at least one."
        )

    even_share = remaining_resource / turns_remaining

    if strategy == ResourceStrategy.CONSERVATIVE:
        return int(even_share)

    if strategy == ResourceStrategy.BALANCED:
        return ceil(even_share)

    if strategy == ResourceStrategy.AGGRESSIVE:
        return min(
            remaining_resource,
            max(1, ceil(even_share * 2)),
        )

    raise ValueError(
        "Unsupported resource strategy."
    )


def calculate_turn_resource_budget(
    resources: HeroResourceState,
    turns_remaining: int,
    strategy: ResourceStrategy,
) -> HeroResourceState:
    return HeroResourceState(
        remaining_might=calculate_resource_budget(
            remaining_resource=resources.remaining_might,
            turns_remaining=turns_remaining,
            strategy=strategy,
        ),
        remaining_will=calculate_resource_budget(
            remaining_resource=resources.remaining_will,
            turns_remaining=turns_remaining,
            strategy=strategy,
        ),
        remaining_fate=calculate_resource_budget(
            remaining_resource=resources.remaining_fate,
            turns_remaining=turns_remaining,
            strategy=strategy,
        ),
    )


def calculate_turn_will_budget(
    remaining_will: int,
    turns_remaining: int,
    strategy: ResourceStrategy,
) -> int:
    return calculate_resource_budget(
        remaining_resource=remaining_will,
        turns_remaining=turns_remaining,
        strategy=strategy,
    )

def allocation_fits_turn_budget(
    budget: HeroResourceState,
    allocations: tuple[ResourceAllocation, ...],
) -> bool:
    total_might = sum(
        allocation.might
        for allocation in allocations
    )
    total_will = sum(
        allocation.will
        for allocation in allocations
    )
    total_fate = sum(
        allocation.fate
        for allocation in allocations
    )

    return (
        total_might <= budget.remaining_might
        and total_will <= budget.remaining_will
        and total_fate <= budget.remaining_fate
    )

def strategy_allows_allocations(
    resources: HeroResourceState,
    turns_remaining: int,
    strategy: ResourceStrategy,
    allocations: tuple[ResourceAllocation, ...],
) -> bool:
    budget = calculate_turn_resource_budget(
        resources=resources,
        turns_remaining=turns_remaining,
        strategy=strategy,
    )

    return allocation_fits_turn_budget(
        budget=budget,
        allocations=allocations,
    )