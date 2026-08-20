from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from resource_owner import ResourceOwner


def test_owned_hero_resource_state_stores_owner_and_resources():
    owner = ResourceOwner(
        profile_id="DG_NEC",
        instance_index=1,
    )

    resources = HeroResourceState(
        remaining_might=3,
        remaining_will=25,
        remaining_fate=0,
    )

    owned_state = OwnedHeroResourceState(
        owner=owner,
        resources=resources,
    )

    assert owned_state.owner == owner
    assert owned_state.resources == resources


def test_owned_hero_resource_state_preserves_owner_key():
    owned_state = OwnedHeroResourceState(
        owner=ResourceOwner(
            profile_id="DG_SM",
            instance_index=2,
        ),
        resources=HeroResourceState(
            remaining_might=1,
            remaining_will=1,
            remaining_fate=1,
        ),
    )

    assert owned_state.owner.key == "DG_SM:2"


def test_equivalent_owned_hero_resource_states_are_equal():
    first_state = OwnedHeroResourceState(
        owner=ResourceOwner(
            profile_id="DG_WK",
            instance_index=1,
        ),
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=10,
            remaining_fate=2,
        ),
    )

    second_state = OwnedHeroResourceState(
        owner=ResourceOwner(
            profile_id="DG_WK",
            instance_index=1,
        ),
        resources=HeroResourceState(
            remaining_might=3,
            remaining_will=10,
            remaining_fate=2,
        ),
    )

    assert first_state == second_state


def test_different_owners_with_same_resources_remain_distinct():
    first_state = OwnedHeroResourceState(
        owner=ResourceOwner(
            profile_id="DG_SM",
            instance_index=1,
        ),
        resources=HeroResourceState(
            remaining_might=1,
            remaining_will=1,
            remaining_fate=1,
        ),
    )

    second_state = OwnedHeroResourceState(
        owner=ResourceOwner(
            profile_id="DG_SM",
            instance_index=2,
        ),
        resources=HeroResourceState(
            remaining_might=1,
            remaining_will=1,
            remaining_fate=1,
        ),
    )

    assert first_state != second_state