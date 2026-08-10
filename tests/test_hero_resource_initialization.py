from configured_profile import ConfiguredProfile
from hero_resource_initialization import (
    get_initial_hero_resource_state,
)
from hero_resource_state import HeroResourceState
from test_profiles import create_test_profile


def test_initial_hero_resource_state_uses_profile_resources():
    profile = create_test_profile(
        profile_id="HERO",
    )

    profile.might = 3
    profile.will = 2
    profile.fate = 1

    configured_profile = ConfiguredProfile(
        profile=profile,
    )

    assert get_initial_hero_resource_state(
        configured_profile
    ) == HeroResourceState(
        remaining_might=3,
        remaining_will=2,
        remaining_fate=1,
    )