from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_totals import (
    calculate_owned_resource_allocation_totals,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_allocations_for_same_owner_and_resource_type_are_summed():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    allocations = (
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=2,
        ),
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.TAKE_FATE,
            amount=1,
        ),
    )

    result = calculate_owned_resource_allocation_totals(
        allocations,
    )

    assert result == {
        (owner, ResourceType.WILL): 3,
    }


def test_different_resource_types_are_not_combined():
    owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    allocations = (
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.MIGHT,
            resource_use=ResourceUse.MODIFY_DUEL,
            amount=1,
        ),
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=2,
        ),
    )

    result = calculate_owned_resource_allocation_totals(
        allocations,
    )

    assert result == {
        (owner, ResourceType.MIGHT): 1,
        (owner, ResourceType.WILL): 2,
    }


def test_different_owners_are_not_combined():
    first_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=1,
    )

    second_owner = ResourceOwner(
        profile_id="DG_SM",
        instance_index=2,
    )

    allocations = (
        OwnedResourceAllocation(
            owner=first_owner,
            resource_type=ResourceType.MIGHT,
            resource_use=ResourceUse.MODIFY_DUEL,
            amount=1,
        ),
        OwnedResourceAllocation(
            owner=second_owner,
            resource_type=ResourceType.MIGHT,
            resource_use=ResourceUse.MODIFY_DUEL,
            amount=1,
        ),
    )

    result = calculate_owned_resource_allocation_totals(
        allocations,
    )

    assert result == {
        (first_owner, ResourceType.MIGHT): 1,
        (second_owner, ResourceType.MIGHT): 1,
    }


def test_empty_allocations_return_empty_totals():
    result = calculate_owned_resource_allocation_totals(
        (),
    )

    assert result == {}