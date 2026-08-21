from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_strategy_budget import (
    owned_strategy_allows_allocations,
)
from resource_owner import ResourceOwner
from resource_strategy import ResourceStrategy
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_balanced_strategy_allows_owner_allocation_within_budget():
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
    )

    assert owned_strategy_allows_allocations(
        states=(state,),
        turns_remaining=3,
        strategy=ResourceStrategy.BALANCED,
        allocations=allocations,
    )


def test_balanced_strategy_rejects_owner_allocation_above_budget():
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
            amount=3,
        ),
    )

    assert not owned_strategy_allows_allocations(
        states=(state,),
        turns_remaining=3,
        strategy=ResourceStrategy.BALANCED,
        allocations=allocations,
    )


def test_competing_uses_share_same_owner_turn_budget():
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
            amount=1,
        ),
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.TAKE_FATE,
            amount=1,
        ),
    )

    assert owned_strategy_allows_allocations(
        states=(state,),
        turns_remaining=3,
        strategy=ResourceStrategy.BALANCED,
        allocations=allocations,
    )


def test_different_owners_have_independent_turn_budgets():
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
            amount=2,
        ),
        OwnedResourceAllocation(
            owner=witch_king_owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=1,
        ),
    )

    assert owned_strategy_allows_allocations(
        states=states,
        turns_remaining=3,
        strategy=ResourceStrategy.BALANCED,
        allocations=allocations,
    )


def test_unknown_owner_is_rejected_by_strategy_budget():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    allocations = (
        OwnedResourceAllocation(
            owner=owner,
            resource_type=ResourceType.WILL,
            resource_use=ResourceUse.CAST_SPELL,
            amount=1,
        ),
    )

    assert not owned_strategy_allows_allocations(
        states=(),
        turns_remaining=3,
        strategy=ResourceStrategy.BALANCED,
        allocations=allocations,
    )