import pytest

from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_legality import (
    validate_owned_resource_allocation,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_default_legal_allocation_is_accepted():
    owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    allocation = OwnedResourceAllocation(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
        amount=1,
    )

    validate_owned_resource_allocation(
        allocation=allocation,
        permissions=(),
        conversions=(),
    )


def test_explicit_owner_permission_allows_special_allocation():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    allocation = OwnedResourceAllocation(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        amount=1,
    )

    permission = OwnedResourceUsePermission(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
    )

    validate_owned_resource_allocation(
        allocation=allocation,
        permissions=(permission,),
        conversions=(),
    )


def test_matching_conversion_allows_special_allocation():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    allocation = OwnedResourceAllocation(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        amount=1,
    )

    conversion = OwnedResourceConversion(
        owner=owner,
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    validate_owned_resource_allocation(
        allocation=allocation,
        permissions=(),
        conversions=(conversion,),
    )


def test_illegal_allocation_is_rejected():
    owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    allocation = OwnedResourceAllocation(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        amount=1,
    )

    with pytest.raises(
        ValueError,
        match="Owned resource allocation is not permitted.",
    ):
        validate_owned_resource_allocation(
            allocation=allocation,
            permissions=(),
            conversions=(),
        )


def test_conversion_for_different_owner_does_not_allow_allocation():
    allocation_owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    conversion_owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    allocation = OwnedResourceAllocation(
        owner=allocation_owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.TAKE_FATE,
        amount=1,
    )

    conversion = OwnedResourceConversion(
        owner=conversion_owner,
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Owned resource allocation is not permitted.",
    ):
        validate_owned_resource_allocation(
            allocation=allocation,
            permissions=(),
            conversions=(conversion,),
        )