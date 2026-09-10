from army import Army
from configured_profile import ConfiguredProfile
from hero_resource_state import HeroResourceState
from owned_army_resource_initialization import (
    get_initial_owned_hero_resource_states,
)
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_application import (
    apply_owned_resource_allocations,
)
from owned_resource_conversion_initialization import (
    get_initial_owned_resource_conversions,
)
from owned_resource_use_permission_initialization import (
    get_initial_owned_resource_use_permissions,
)
from profiles import Profile
from resource_conversion import ResourceConversion
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def make_profile(
    *,
    profile_id: str,
    might: int = 1,
    will: int = 1,
    fate: int = 1,
    special_resource_permissions=(),
    special_resource_conversions=(),
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=50,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=might,
        will=will,
        fate=fate,
        max_in_army=0,
        special_resource_permissions=special_resource_permissions,
        special_resource_conversions=special_resource_conversions,
    )


def test_dev063_repeated_profile_instances_get_distinct_resource_owners():
    profile = make_profile(
        profile_id="GENERIC_HERO",
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=2,
    )

    states = get_initial_owned_hero_resource_states(
        army,
    )

    assert len(states) == 2

    assert states[0].owner.fielded_model_id == (
        "GENERIC_HERO:1:1"
    )

    assert states[1].owner.fielded_model_id == (
        "GENERIC_HERO:1:2"
    )

    assert states[0].owner != states[1].owner


def test_dev063_same_profile_different_configurations_do_not_collide():
    profile = make_profile(
        profile_id="GENERIC_HERO",
    )

    first_configuration = ConfiguredProfile(
        profile=profile,
    )

    second_configuration = ConfiguredProfile(
        profile=profile,
    )

    army = Army()

    army.add_configured_profile(
        first_configuration,
        quantity=1,
    )

    army.add_configured_profile(
        second_configuration,
        quantity=1,
    )

    states = get_initial_owned_hero_resource_states(
        army,
    )

    assert len(states) == 2

    assert states[0].owner.fielded_model_id == (
        "GENERIC_HERO:1:1"
    )

    assert states[1].owner.fielded_model_id == (
        "GENERIC_HERO:2:1"
    )

    assert states[0].owner != states[1].owner


def test_dev063_spending_on_one_owner_does_not_change_another_owner():
    profile = make_profile(
        profile_id="GENERIC_HERO",
        might=2,
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=2,
    )

    states = get_initial_owned_hero_resource_states(
        army,
    )

    first_state = states[0]
    second_state = states[1]

    allocations = (
        OwnedResourceAllocation(
            owner=first_state.owner,
            resource_type=ResourceType.MIGHT,
            resource_use=ResourceUse.MODIFY_DUEL,
            amount=1,
        ),
    )

    updated_states = apply_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=(),
        conversions=(),
    )

    assert updated_states[0].resources == HeroResourceState(
        remaining_might=1,
        remaining_will=1,
        remaining_fate=1,
    )

    assert updated_states[1].resources == HeroResourceState(
        remaining_might=2,
        remaining_will=1,
        remaining_fate=1,
    )

    assert second_state.resources == HeroResourceState(
        remaining_might=2,
        remaining_will=1,
        remaining_fate=1,
    )


def test_dev063_permissions_are_owned_by_exact_fielded_model():
    profile = make_profile(
        profile_id="GENERIC_HERO",
        special_resource_permissions=(
            (
                ResourceType.WILL,
                ResourceUse.TAKE_FATE,
            ),
        ),
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=2,
    )

    permissions = get_initial_owned_resource_use_permissions(
        army,
    )

    owner_ids = {
        permission.owner.fielded_model_id
        for permission in permissions
    }

    assert owner_ids == {
        "GENERIC_HERO:1:1",
        "GENERIC_HERO:1:2",
    }


def test_dev063_conversions_are_owned_by_exact_fielded_model():
    conversion = ResourceConversion(
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    profile = make_profile(
        profile_id="GENERIC_HERO",
        special_resource_conversions=(
            conversion,
        ),
    )

    army = Army()
    army.add_profile(
        profile,
        quantity=2,
    )

    conversions = get_initial_owned_resource_conversions(
        army,
    )

    owner_ids = {
        owned_conversion.owner.fielded_model_id
        for owned_conversion in conversions
    }

    assert owner_ids == {
        "GENERIC_HERO:1:1",
        "GENERIC_HERO:1:2",
    }