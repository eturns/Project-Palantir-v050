from army import Army
from army_resource_state import ArmyResourceState
from army_resource_totals import calculate_army_resource_totals
from hero_resource_state import HeroResourceState
from owned_army_resource_aggregation import (
    aggregate_owned_hero_resource_states,
)
from owned_army_resource_initialization import (
    get_initial_owned_hero_resource_states,
)
from owned_hero_resource_state import OwnedHeroResourceState
from profiles import Profile
from resource_owner import ResourceOwner


def make_profile(
    profile_id: str,
    might: int,
    will: int,
    fate: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=80,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="4+",
        might=might,
        will=will,
        fate=fate,
        max_in_army=0,
    )


def test_aggregates_owned_resource_states_into_army_resource_state():
    owned_states = (
        OwnedHeroResourceState(
            owner=ResourceOwner(
                profile_id="DG_NEC",
                instance_index=1,
            ),
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=25,
                remaining_fate=0,
            ),
        ),
        OwnedHeroResourceState(
            owner=ResourceOwner(
                profile_id="DG_WK",
                instance_index=1,
            ),
            resources=HeroResourceState(
                remaining_might=3,
                remaining_will=10,
                remaining_fate=2,
            ),
        ),
    )

    result = aggregate_owned_hero_resource_states(
        owned_states,
    )

    assert result == ArmyResourceState(
        might=6,
        will=35,
        fate=2,
    )


def test_aggregation_includes_repeated_profile_instances():
    owned_states = (
        OwnedHeroResourceState(
            owner=ResourceOwner(
                profile_id="DG_SM",
                instance_index=1,
            ),
            resources=HeroResourceState(
                remaining_might=1,
                remaining_will=1,
                remaining_fate=1,
            ),
        ),
        OwnedHeroResourceState(
            owner=ResourceOwner(
                profile_id="DG_SM",
                instance_index=2,
            ),
            resources=HeroResourceState(
                remaining_might=1,
                remaining_will=1,
                remaining_fate=1,
            ),
        ),
    )

    result = aggregate_owned_hero_resource_states(
        owned_states,
    )

    assert result == ArmyResourceState(
        might=2,
        will=2,
        fate=2,
    )


def test_empty_owned_resource_collection_aggregates_to_zero():
    result = aggregate_owned_hero_resource_states(())

    assert result == ArmyResourceState(
        might=0,
        will=0,
        fate=0,
    )


def test_owner_aware_initialization_matches_existing_army_resource_totals():
    army = Army()

    necromancer = make_profile(
        profile_id="DG_NEC",
        might=3,
        will=25,
        fate=0,
    )

    slayer = make_profile(
        profile_id="DG_SM",
        might=1,
        will=1,
        fate=1,
    )

    army.add_profile(
        necromancer,
        quantity=1,
    )

    army.add_profile(
        slayer,
        quantity=2,
    )

    existing_totals = calculate_army_resource_totals(
        army,
    )

    owned_states = get_initial_owned_hero_resource_states(
        army,
    )

    owner_aware_totals = aggregate_owned_hero_resource_states(
        owned_states,
    )

    assert owner_aware_totals == existing_totals