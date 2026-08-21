import pytest

from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_owned_resource_allocation_stores_owner_resource_use_and_amount():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    allocation = OwnedResourceAllocation(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
        amount=2,
    )

    assert allocation.owner == owner
    assert allocation.resource_type == ResourceType.WILL
    assert allocation.resource_use == ResourceUse.CAST_SPELL
    assert allocation.amount == 2


def test_equivalent_owned_resource_allocations_are_equal():
    allocation_a = OwnedResourceAllocation(
        owner=ResourceOwner(
            profile_id="DG_NEC",
            instance_index=1,
        ),
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
        amount=2,
    )

    allocation_b = OwnedResourceAllocation(
        owner=ResourceOwner(
            profile_id="DG_NEC",
            instance_index=1,
        ),
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
        amount=2,
    )

    assert allocation_a == allocation_b


def test_allocation_for_different_owner_is_distinct():
    first = OwnedResourceAllocation(
        owner=ResourceOwner(
            profile_id="DG_SM",
            instance_index=1,
        ),
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.MODIFY_DUEL,
        amount=1,
    )

    second = OwnedResourceAllocation(
        owner=ResourceOwner(
            profile_id="DG_SM",
            instance_index=2,
        ),
        resource_type=ResourceType.MIGHT,
        resource_use=ResourceUse.MODIFY_DUEL,
        amount=1,
    )

    assert first != second


def test_owned_resource_allocation_rejects_negative_amount():
    with pytest.raises(
        ValueError,
        match="Allocated resource amount cannot be negative.",
    ):
        OwnedResourceAllocation(
            owner=ResourceOwner(
                profile_id="DG_NEC",
                instance_index=1,
            ),
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=-1,
        )