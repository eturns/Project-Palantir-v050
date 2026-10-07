from configured_profile import ConfiguredProfile
from hero_resource_initialization import (
    get_initial_hero_resource_state,
)
from hero_resource_state import HeroResourceState
from test_profiles import create_test_profile
from configured_state_effect import ConfiguredStateEffect
from profile_option import ProfileOption

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

def test_initial_hero_resource_state_uses_configured_resource_overrides():
    profile = create_test_profile(
        profile_id="HERO",
    )

    profile.might = 3
    profile.will = 2
    profile.fate = 1

    option = ProfileOption(
        id="RESOURCE_OVERRIDE",
        name="Resource Override",
        points=0,
        configured_state_effects=(
            ConfiguredStateEffect(
                might_override=1,
                will_override=4,
                fate_override=2,
            ),
        ),
    )

    profile.profile_options.append(
        option
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert get_initial_hero_resource_state(
        configured_profile
    ) == HeroResourceState(
        remaining_might=1,
        remaining_will=4,
        remaining_fate=2,
    )