from fractions import Fraction

from configured_profile import ConfiguredProfile
from hero_resource_initialization import (
    get_initial_hero_resource_state,
)
from hero_resource_spending import spend_will
from profiles import Profile
from resurrection_probability import (
    get_resurrection_probability_with_resource_state,
)


def create_test_profile(
    profile_id: str,
) -> Profile:
    return Profile(
        id=profile_id,
        name="Test Profile",
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=4,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=3,
        will=20,
        fate=1,
        max_in_army=0,
    )


def test_resource_state_foundation_regression():
    configured_profile = ConfiguredProfile(
        profile=create_test_profile(
            "NECROMANCER",
        )
    )

    initial_state = get_initial_hero_resource_state(
        configured_profile
    )

    assert initial_state.remaining_might == 3
    assert initial_state.remaining_will == 20
    assert initial_state.remaining_fate == 1

    spent_state = spend_will(
        initial_state,
        amount=1,
    )

    assert initial_state.remaining_will == 20
    assert spent_state.remaining_will == 19

    probability = (
        get_resurrection_probability_with_resource_state(
            necromancer_resources=initial_state,
            distance_inches=18,
            will_points_available_to_spend=1,
        )
    )

    assert probability == Fraction(1, 1)