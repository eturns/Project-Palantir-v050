from army import Army
from owned_army_resource_initialization import (
    get_initial_owned_hero_resource_states,
)
from profiles import Profile


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


def test_builds_one_owned_resource_state_per_model_instance():
    army = Army()

    slayer = make_profile(
        profile_id="DG_SM",
        might=1,
        will=1,
        fate=1,
    )

    army.add_profile(
        slayer,
        quantity=2,
    )

    owned_states = get_initial_owned_hero_resource_states(
        army,
    )

    assert len(owned_states) == 2


def test_repeated_profiles_receive_distinct_deterministic_owner_keys():
    army = Army()

    slayer = make_profile(
        profile_id="DG_SM",
        might=1,
        will=1,
        fate=1,
    )

    army.add_profile(
        slayer,
        quantity=2,
    )

    owned_states = get_initial_owned_hero_resource_states(
        army,
    )

    assert tuple(
        state.owner.key
        for state in owned_states
    ) == (
        "DG_SM:1",
        "DG_SM:2",
    )


def test_each_owned_state_uses_the_profiles_resources():
    army = Army()

    witch_king = make_profile(
        profile_id="DG_WK",
        might=3,
        will=10,
        fate=2,
    )

    army.add_profile(
        witch_king,
        quantity=1,
    )

    owned_states = get_initial_owned_hero_resource_states(
        army,
    )

    assert owned_states[0].resources.remaining_might == 3
    assert owned_states[0].resources.remaining_will == 10
    assert owned_states[0].resources.remaining_fate == 2