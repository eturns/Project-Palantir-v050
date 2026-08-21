import pytest

from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_validation import (
    validate_owned_resource_allocations,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_competing_uses_can_share_same_finite_source_pool():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    state = OwnedHeroResourceState(
        owner=owner,
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=5,
            remaining_fate=0,
        ),
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

    conversion = OwnedResourceConversion(
        owner=owner,
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    validate_owned_resource_allocations(
        states=(state,),
        allocations=allocations,
        permissions=(),
        conversions=(conversion,),
    )


def test_competing_uses_cannot_overspend_same_source_pool():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    state = OwnedHeroResourceState(
        owner=owner,
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=2,
            remaining_fate=0,
        ),
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

    conversion = OwnedResourceConversion(
        owner=owner,
        conversion=ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Owned resource allocations exceed remaining Will.",
    ):
        validate_owned_resource_allocations(
            states=(state,),
            allocations=allocations,
            permissions=(),
            conversions=(conversion,),
        )


def test_allocation_cannot_use_unknown_owner_state():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    allocation = OwnedResourceAllocation(
        owner=owner,
        resource_type=ResourceType.WILL,
        resource_use=ResourceUse.CAST_SPELL,
        amount=1,
    )

    with pytest.raises(
        ValueError,
        match="No resource state exists for allocation owner.",
    ):
        validate_owned_resource_allocations(
            states=(),
            allocations=(allocation,),
            permissions=(),
            conversions=(),
        )


def test_different_owners_validate_against_their_own_pools():
    necromancer_owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    witch_king_owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    states = (
        OwnedHeroResourceState(
            owner=necromancer_owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=5,
                remaining_fate=0,
            ),
        ),
        OwnedHeroResourceState(
            owner=witch_king_owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=3,
                remaining_fate=2,
            ),
        ),
    )

    allocations = (
        OwnedResourceAllocation(
            owner=necromancer_owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=4,
        ),
        OwnedResourceAllocation(
            owner=witch_king_owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=2,
        ),
    )

    validate_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
    )