import pytest

from hero_resource_state import HeroResourceState

from resource_allocation import (
    ResourceAllocation,
    apply_resource_allocations,
    validate_resource_allocations,
)
from resource_spend_domain import ResourceSpendDomain


def test_resource_allocation_stores_domain_and_resources():
    allocation = ResourceAllocation(
        domain=ResourceSpendDomain.MAGIC,
        might=1,
        will=2,
    )

    assert allocation.domain == ResourceSpendDomain.MAGIC
    assert allocation.might == 1
    assert allocation.will == 2
    assert allocation.fate == 0


def test_resource_allocation_rejects_negative_might():
    with pytest.raises(
        ValueError,
        match="Allocated Might cannot be negative.",
    ):
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=-1,
        )


def test_resource_allocation_rejects_negative_will():
    with pytest.raises(
        ValueError,
        match="Allocated Will cannot be negative.",
    ):
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            will=-1,
        )


def test_resource_allocation_rejects_negative_fate():
    with pytest.raises(
        ValueError,
        match="Allocated Fate cannot be negative.",
    ):
        ResourceAllocation(
            domain=ResourceSpendDomain.DEFENCE,
            fate=-1,
        )

def test_resource_allocations_can_share_finite_resources():
    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=4,
        remaining_fate=2,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=1,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            might=1,
            will=2,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.DEFENCE,
            might=1,
            fate=2,
        ),
    )

    validate_resource_allocations(
        resources=resources,
        allocations=allocations,
    )


def test_resource_allocations_cannot_overspend_might():
    resources = HeroResourceState(
        remaining_might=2,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=1,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            might=2,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Allocated Might exceeds remaining Might.",
    ):
        validate_resource_allocations(
            resources=resources,
            allocations=allocations,
        )


def test_resource_allocations_cannot_overspend_will():
    resources = HeroResourceState(
        remaining_will=2,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            will=2,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.DEFENCE,
            will=1,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Allocated Will exceeds remaining Will.",
    ):
        validate_resource_allocations(
            resources=resources,
            allocations=allocations,
        )


def test_resource_allocations_cannot_overspend_fate():
    resources = HeroResourceState(
        remaining_fate=1,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.DEFENCE,
            fate=2,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Allocated Fate exceeds remaining Fate.",
    ):
        validate_resource_allocations(
            resources=resources,
            allocations=allocations,
        )

def test_apply_resource_allocations_returns_remaining_resources():
    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=4,
        remaining_fate=2,
    )

    allocations = (
        ResourceAllocation(
            domain=ResourceSpendDomain.COMBAT,
            might=1,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.MAGIC,
            might=1,
            will=2,
        ),
        ResourceAllocation(
            domain=ResourceSpendDomain.DEFENCE,
            fate=1,
        ),
    )

    result = apply_resource_allocations(
        resources=resources,
        allocations=allocations,
    )

    assert result == HeroResourceState(
        remaining_might=1,
        remaining_will=2,
        remaining_fate=1,
    )


def test_apply_resource_allocations_does_not_mutate_original_state():
    resources = HeroResourceState(
        remaining_might=2,
        remaining_will=3,
        remaining_fate=1,
    )

    apply_resource_allocations(
        resources=resources,
        allocations=(
            ResourceAllocation(
                domain=ResourceSpendDomain.MAGIC,
                will=1,
            ),
        ),
    )

    assert resources == HeroResourceState(
        remaining_might=2,
        remaining_will=3,
        remaining_fate=1,
    )