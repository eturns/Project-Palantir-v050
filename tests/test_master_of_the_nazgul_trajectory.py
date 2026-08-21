from hero_resource_state import HeroResourceState
from master_of_the_nazgul_aura import (
    get_master_of_the_nazgul_aura_range_inches,
)
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


def test_master_aura_changes_when_trajectory_crosses_will_thresholds():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    initial_states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=21,
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
                amount=1,
            ),
        ),
        (
            OwnedResourceAllocation(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.CAST_SPELL,
                amount=10,
            ),
        ),
        (
            OwnedResourceAllocation(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.CAST_SPELL,
                amount=1,
            ),
        ),
    )

    trajectory = calculate_owned_resource_trajectory(
        initial_states=initial_states,
        allocations_by_turn=allocations_by_turn,
        permissions=(),
        conversions=(),
    )

    aura_ranges = tuple(
        get_master_of_the_nazgul_aura_range_inches(
            states[0].resources,
        )
        for states in trajectory
    )

    assert aura_ranges == (
        18,  # 21 Will
        18,  # 20 Will
        12,  # 19 Will
        6,  # 9 Will
        6, # 8 Will
    )

    assert tuple(
        states[0].resources.remaining_will
        for states in trajectory
    ) == (
        21,
        20,
        19,
        9,
        8,
    )