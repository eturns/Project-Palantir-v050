import pytest
from hero_resource_state import HeroResourceState
from resource_strategy import ResourceStrategy
from resource_strategy_budget import (
    allocation_fits_turn_budget,
    calculate_turn_resource_budget,
    calculate_turn_will_budget,
    strategy_allows_allocations,
)
from resource_allocation import ResourceAllocation
from resource_spend_domain import ResourceSpendDomain


def test_conservative_strategy_preserves_will():
    assert calculate_turn_will_budget(
        remaining_will=5,
        turns_remaining=3,
        strategy=ResourceStrategy.CONSERVATIVE,
    ) == 1


def test_balanced_strategy_uses_even_share():
    assert calculate_turn_will_budget(
        remaining_will=5,
        turns_remaining=3,
        strategy=ResourceStrategy.BALANCED,
    ) == 2


def test_aggressive_strategy_front_loads_will():
    assert calculate_turn_will_budget(
        remaining_will=5,
        turns_remaining=3,
        strategy=ResourceStrategy.AGGRESSIVE,
    ) == 4


def test_budget_never_exceeds_remaining_will():
    assert calculate_turn_will_budget(
        remaining_will=1,
        turns_remaining=8,
        strategy=ResourceStrategy.AGGRESSIVE,
    ) == 1


def test_budget_rejects_zero_turns_remaining():
    with pytest.raises(
        ValueError,
        match="Turns remaining must be at least one.",
    ):
        calculate_turn_will_budget(
            remaining_will=3,
            turns_remaining=0,
            strategy=ResourceStrategy.BALANCED,
        )

def test_turn_resource_budget_applies_strategy_to_all_resources():
    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=5,
        remaining_fate=2,
    )

    budget = calculate_turn_resource_budget(
        resources=resources,
        turns_remaining=3,
        strategy=ResourceStrategy.BALANCED,
    )

    assert budget == HeroResourceState(
        remaining_might=1,
        remaining_will=2,
        remaining_fate=1,
    )


def test_turn_resource_budget_does_not_mutate_resources():
    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=5,
        remaining_fate=2,
    )

    calculate_turn_resource_budget(
        resources=resources,
        turns_remaining=3,
        strategy=ResourceStrategy.AGGRESSIVE,
    )

    assert resources == HeroResourceState(
        remaining_might=3,
        remaining_will=5,
        remaining_fate=2,
    )

def test_allocation_fits_balanced_turn_budget():
    budget = HeroResourceState(
        remaining_might=1,
        remaining_will=2,
        remaining_fate=1,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=1,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            will=2,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.DEFENCE,
            fate=1,
        ),
    )

    assert allocation_fits_turn_budget(
        budget=budget,
        allocations=allocations,
    )


def test_allocation_exceeding_turn_budget_is_rejected():
    budget = HeroResourceState(
        remaining_might=1,
        remaining_will=1,
        remaining_fate=1,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=1,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            might=1,
            will=1,
        ),
    )

    assert not allocation_fits_turn_budget(
        budget=budget,
        allocations=allocations,
    )

def test_conservative_strategy_rejects_front_loaded_spend():
    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=5,
        remaining_fate=2,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=2,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            will=2,
        ),
    )

    assert not strategy_allows_allocations(
        resources=resources,
        turns_remaining=3,
        strategy=ResourceStrategy.CONSERVATIVE,
        allocations=allocations,
    )


def test_aggressive_strategy_allows_front_loaded_spend():
    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=5,
        remaining_fate=2,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=2,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            will=2,
        ),
    )

    assert strategy_allows_allocations(
        resources=resources,
        turns_remaining=3,
        strategy=ResourceStrategy.AGGRESSIVE,
        allocations=allocations,
    )