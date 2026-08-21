from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_trajectory import (
    calculate_owned_resource_trajectory,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_multi_turn_trajectory_uses_previous_turn_state():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    initial_states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=5,
                remaining_fate=0,
            ),
        ),
    )

    allocations_by_turn = (
        (
            OwnedResourceAllocation(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.CAST_SPELL,
                amount=1,
            ),
        ),
        (
            OwnedResourceAllocation(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.CAST_SPELL,
                amount=2,
            ),
        ),
    )

    result = calculate_owned_resource_trajectory(
        initial_states=initial_states,
        allocations_by_turn=allocations_by_turn,
        permissions=(),
        conversions=(),
    )

    assert result == (
        initial_states,
        (
            OwnedHeroResourceState(
                owner=owner,
                resources=HeroResourceState(
                    remaining_might=3,
                    remaining_will=4,
                    remaining_fate=0,
                ),
            ),
        ),
        (
            OwnedHeroResourceState(
                owner=owner,
                resources=HeroResourceState(
                    remaining_might=3,
                    remaining_will=2,
                    remaining_fate=0,
                ),
            ),
        ),
    )


def test_multi_turn_trajectory_preserves_owner_isolation():
    necromancer_owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    witch_king_owner = ResourceOwner(
        profile_id="DG_WK",
        instance_index=1,
    )

    initial_states = (
        OwnedHeroResourceState(
            owner=necromancer_owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=4,
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

    allocations_by_turn = (
        (
            OwnedResourceAllocation(
                owner=necromancer_owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.CAST_SPELL,
                amount=1,
            ),
        ),
        (),
    )

    result = calculate_owned_resource_trajectory(
        initial_states=initial_states,
        allocations_by_turn=allocations_by_turn,
        permissions=(),
        conversions=(),
    )

    assert result[1][1] == initial_states[1]
    assert result[2][1] == initial_states[1]