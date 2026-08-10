from model_platform import Platform, PlatformType
from profile_option_platform_assignment import (
    ProfileOptionPlatformAssignment,
)


def test_profile_option_platform_assignment_stores_platform():
    chariot = Platform(
        id="PLATFORM_IRON_HILLS_CHARIOT",
        name="Iron Hills Chariot",
        platform_type=PlatformType.CHARIOT,
    )

    assignment = ProfileOptionPlatformAssignment(
        platform=chariot,
    )

    assert assignment.platform is chariot


def test_profile_option_platform_assignment_is_immutable():
    chariot = Platform(
        id="PLATFORM_IRON_HILLS_CHARIOT",
        name="Iron Hills Chariot",
        platform_type=PlatformType.CHARIOT,
    )

    mumak = Platform(
        id="PLATFORM_WAR_MUMAK",
        name="War Mumak",
        platform_type=PlatformType.WAR_BEAST,
    )

    assignment = ProfileOptionPlatformAssignment(
        platform=chariot,
    )

    try:
        assignment.platform = mumak
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Expected ProfileOptionPlatformAssignment "
            "to be immutable."
        )