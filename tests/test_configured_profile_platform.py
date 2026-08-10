from configured_profile import ConfiguredProfile
from model_platform import Platform, PlatformType
from profile_option import ProfileOption
from profile_option_platform_assignment import (
    ProfileOptionPlatformAssignment,
)
from profiles import Profile


def create_profile() -> Profile:
    return Profile(
        id="TEST_PROFILE",
        name="Test Profile",
        points=80,
        movement=5,
        fight=5,
        shooting="4+",
        strength=4,
        defence=8,
        attacks=2,
        wounds=2,
        courage="5+",
        intelligence="5+",
        might=2,
        will=1,
        fate=1,
        max_in_army=0,
    )


def test_effective_platform_is_none_by_default():
    configured_profile = ConfiguredProfile(
        profile=create_profile(),
    )

    assert configured_profile.effective_platform is None


def test_effective_platform_uses_selected_option():
    platform = Platform(
        id="PLATFORM_TEST_CHARIOT",
        name="Test Chariot",
        platform_type=PlatformType.CHARIOT,
    )

    option = ProfileOption(
        id="OPTION_CHARIOT",
        name="Chariot",
        points=170,
        platform_assignments=(
            ProfileOptionPlatformAssignment(
                platform=platform,
            ),
        ),
    )

    profile = create_profile()
    profile.profile_options.append(option)

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(option,),
    )

    assert configured_profile.effective_platform is (
        platform
    )


def test_rejects_multiple_option_platforms():
    first_platform = Platform(
        id="PLATFORM_FIRST",
        name="First Chariot",
        platform_type=PlatformType.CHARIOT,
    )
    second_platform = Platform(
        id="PLATFORM_SECOND",
        name="Second Chariot",
        platform_type=PlatformType.CHARIOT,
    )

    first_option = ProfileOption(
        id="OPTION_FIRST",
        name="First Chariot",
        points=100,
        platform_assignments=(
            ProfileOptionPlatformAssignment(
                platform=first_platform,
            ),
        ),
    )
    second_option = ProfileOption(
        id="OPTION_SECOND",
        name="Second Chariot",
        points=100,
        platform_assignments=(
            ProfileOptionPlatformAssignment(
                platform=second_platform,
            ),
        ),
    )

    profile = create_profile()
    profile.profile_options.extend(
        [
            first_option,
            second_option,
        ]
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            first_option,
            second_option,
        ),
    )

    try:
        configured_profile.effective_platform
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError for multiple "
            "Platforms."
        )