from army import Army
from army_model_state_initialization import (
    get_initial_army_model_state,
)
from profiles import Profile


def make_profile(
    profile_id: str,
    points: int = 10,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=points,
        movement=6,
        fight=3,
        shooting="4+",
        strength=3,
        defence=4,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_initial_army_model_state_uses_army_model_count():
    army = Army()

    army.add_profile(
        make_profile("A"),
        quantity=3,
    )

    army.add_profile(
        make_profile("B"),
        quantity=2,
    )

    state = get_initial_army_model_state(
        army,
    )

    assert state.starting_models == 5
    assert state.remaining_models == 5


def test_initial_empty_army_model_state_is_zero():
    army = Army()

    state = get_initial_army_model_state(
        army,
    )

    assert state.starting_models == 0
    assert state.remaining_models == 0