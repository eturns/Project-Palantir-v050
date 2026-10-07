from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_application import (
    apply_owned_resource_allocations,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from temporary_resource_grant import (
    TemporaryResourceGrant,
)
import pytest


def test_applies_competing_allocations_to_same_real_source_pool():
    owner = ResourceOwner(
        fielded_model_id="DG_NEC:1:1",
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

    result = apply_owned_resource_allocations(
        states=(state,),
        allocations=allocations,
        permissions=(),
        conversions=(conversion,),
    )

    assert result == (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=2,
                remaining_fate=0,
            ),
        ),
    )


def test_applying_allocations_keeps_different_owners_isolated():
    necromancer_owner = ResourceOwner(
        fielded_model_id="DG_NEC:1:1",
    )

    witch_king_owner = ResourceOwner(
        fielded_model_id="DG_WK:1:1",
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
            amount=2,
        ),
        OwnedResourceAllocation(
            owner=witch_king_owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=1,
        ),
    )

    result = apply_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
    )

    assert result == (
        OwnedHeroResourceState(
            owner=necromancer_owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=3,
                remaining_fate=0,
            ),
        ),
        OwnedHeroResourceState(
            owner=witch_king_owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=2,
                remaining_fate=2,
            ),
        ),
    )


def test_applying_allocations_does_not_mutate_original_states():
    owner = ResourceOwner(
        fielded_model_id="DG_NEC:1:1",
    )

    state = OwnedHeroResourceState(
        owner=owner,
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=5,
            remaining_fate=0,
        ),
    )

    apply_owned_resource_allocations(
        states=(state,),
        allocations=(
            OwnedResourceAllocation(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.CAST_SPELL,
                amount=2,
            ),
        ),
        permissions=(),
        conversions=(),
    )

    assert state.resources == HeroResourceState(
        remaining_might=3,
        remaining_will=5,
        remaining_fate=0,
    )

def test_temporary_might_is_spent_before_persistent_might():
    owner = ResourceOwner(
        fielded_model_id="BOLG:1:1",
    )

    states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=0,
                remaining_fate=0,
            ),
        ),
    )

    allocations = (
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.MIGHT,
            resource_use=ResourceUse.MODIFY_DUEL,
            amount=1,
        ),
    )

    result = apply_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
        temporary_grants=(
            TemporaryResourceGrant(
                owner=owner,
                resource_type=ResourceType.MIGHT,
                amount=1,
            ),
        ),
    )

    assert result[0].resources.remaining_might == 3

def test_temporary_might_only_reduces_persistent_might_after_it_is_exhausted():
    owner = ResourceOwner(
        fielded_model_id="BOLG:1:1",
    )

    states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=0,
                remaining_fate=0,
            ),
        ),
    )

    allocations = (
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.MIGHT,
            resource_use=ResourceUse.MODIFY_DUEL,
            amount=2,
        ),
    )

    result = apply_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
        temporary_grants=(
            TemporaryResourceGrant(
                owner=owner,
                resource_type=ResourceType.MIGHT,
                amount=1,
            ),
        ),
    )

    assert result[0].resources.remaining_might == 2

def test_temporary_might_cannot_be_spent_by_another_owner():
    bolg_owner = ResourceOwner(
        fielded_model_id="BOLG:1:1",
    )

    other_owner = ResourceOwner(
        fielded_model_id="AZOG:1:1",
    )

    states = (
        OwnedHeroResourceState(
            owner=bolg_owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=0,
                remaining_fate=0,
            ),
        ),
        OwnedHeroResourceState(
            owner=other_owner,
            resources=HeroResourceState(
                remaining_might=0,
                remaining_will=0,
                remaining_fate=0,
            ),
        ),
    )

    allocations = (
        OwnedResourceAllocation(
            owner=other_owner,
            resource_type=ResourceType.MIGHT,
            resource_use=ResourceUse.MODIFY_DUEL,
            amount=1,
        ),
    )

    with pytest.raises(
        ValueError,
        match="Owned resource allocations exceed remaining Might.",
    ):
        apply_owned_resource_allocations(
            states=states,
            allocations=allocations,
            permissions=(),
            conversions=(),
            temporary_grants=(
                TemporaryResourceGrant(
                    owner=bolg_owner,
                    resource_type=ResourceType.MIGHT,
                    amount=1,
                ),
            ),
        )