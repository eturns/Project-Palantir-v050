import pytest

from battle_length_assumption import BattleHorizon
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


@pytest.mark.parametrize(
    "horizon",
    (
        BattleHorizon.SHORT,
        BattleHorizon.MEDIUM,
        BattleHorizon.LONG,
    ),
)
def test_owned_resource_trajectory_supports_battle_horizons(
    horizon: BattleHorizon,
):
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    initial_states = (
        OwnedHeroResourceState(
            owner=owner,
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=25,
                remaining_fate=0,
            ),
        ),
    )

    allocations_by_turn = tuple(
        (
            OwnedResourceAllocation(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.CAST_SPELL,
                amount=1,
            ),
        )
        for _ in range(horizon.value)
    )

    result = calculate_owned_resource_trajectory(
        initial_states=initial_states,
        allocations_by_turn=allocations_by_turn,
        permissions=(),
        conversions=(),
    )

    assert len(result) == horizon.value + 1

    assert (
        result[-1][0].resources.remaining_will
        == 25 - horizon.value
    )