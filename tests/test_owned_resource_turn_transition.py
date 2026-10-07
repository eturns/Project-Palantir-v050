from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_turn_transition import (
    apply_owned_resource_turn,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
import pytest
from temporary_resource_grant import (
    TemporaryResourceGrant,
)

def test_turn_transition_applies_allocations_to_owner_state():
    owner = ResourceOwner(
        fielded_model_id="DG_NEC:1:1",
    )

    states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=5,
                remaining_fate=0,
            ),
        ),
    )

    allocations = (
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=2,
        ),
    )

    result = apply_owned_resource_turn(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
    )

    assert result == (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=3,
                remaining_fate=0,
            ),
        ),
    )


def test_turn_transition_keeps_untouched_owner_unchanged():
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
            amount=1,
        ),
    )

    result = apply_owned_resource_turn(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
    )

    assert result[1] == states[1]

def test_unused_temporary_might_does_not_persist_between_turns():
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

    first_turn = apply_owned_resource_turn(
        states=states,
        allocations=(),
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

    with pytest.raises(
        ValueError,
        match="Owned resource allocations exceed remaining Might.",
    ):
        apply_owned_resource_turn(
            states=first_turn,
            allocations=(
                OwnedResourceAllocation(
                    owner=owner,
                    resource_type=ResourceType.MIGHT,
                    resource_use=ResourceUse.MODIFY_DUEL,
                    amount=4,
                ),
            ),
            permissions=(),
            conversions=(),
            temporary_grants=(),
        )