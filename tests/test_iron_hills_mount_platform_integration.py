from configured_profile import ConfiguredProfile
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)
from model_platform_loader import load_platforms
from mount_loader import load_mounts
from profile_option_loader import load_profile_options
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from profile_option_platform_loader import (
    load_profile_option_platform_assignments,
)


def load_iron_hills_profiles():
    return {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }


def test_dain_war_boar_configuration():
    profiles = load_iron_hills_profiles()
    options = load_profile_options(
        profiles=profiles,
    )
    mounts = load_mounts()

    load_profile_option_mount_assignments(
        profile_options=options,
        mounts=mounts,
    )

    configured_profile = ConfiguredProfile(
        profile=profiles["IH_DAIN"],
        selected_options=(
            options["IH_DAIN_WAR_BOAR"],
        ),
    )

    assert configured_profile.points == 185
    assert configured_profile.effective_mount is (
        mounts["MOUNT_WAR_BOAR"]
    )
    assert configured_profile.effective_platform is None


def test_iron_hills_captain_chariot_configuration():
    profiles = load_iron_hills_profiles()
    options = load_profile_options(
        profiles=profiles,
    )
    platforms = load_platforms()

    load_profile_option_platform_assignments(
        profile_options=options,
        platforms=platforms,
    )

    configured_profile = ConfiguredProfile(
        profile=profiles["IH_CAP"],
        selected_options=(
            options["IH_CAP_CHARIOT"],
        ),
    )

    assert configured_profile.points == 250
    assert configured_profile.effective_platform is (
        platforms["PLATFORM_IRON_HILLS_CHARIOT"]
    )
    assert configured_profile.effective_mount is None