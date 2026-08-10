from configured_profile import ConfiguredProfile
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)
from model_platform_loader import load_platforms
from mount_loader import load_mounts
from profile_default_mount_loader import (
    load_profile_default_mounts,
)
from profile_default_wargear_loader import (
    load_profile_default_wargear,
)
from profile_option_loader import load_profile_options
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from profile_option_platform_loader import (
    load_profile_option_platform_assignments,
)
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from wargear_loader import load_wargear


def load_complete_iron_hills_configuration():
    profiles = {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }

    wargear = load_wargear()
    mounts = load_mounts()
    platforms = load_platforms()

    options = load_profile_options(
        profiles=profiles,
    )

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    load_profile_default_mounts(
        profiles=profiles,
        mounts=mounts,
    )

    load_profile_option_wargear_assignments(
        profile_options=options,
        wargear=wargear,
    )

    load_profile_option_mount_assignments(
        profile_options=options,
        mounts=mounts,
    )

    load_profile_option_platform_assignments(
        profile_options=options,
        platforms=platforms,
    )

    return profiles, options, mounts, platforms


def test_all_non_warrior_iron_hills_configurations():
    (
        profiles,
        options,
        mounts,
        platforms,
    ) = load_complete_iron_hills_configuration()

    dain = ConfiguredProfile(
        profile=profiles["IH_DAIN"],
        selected_options=(
            options["IH_DAIN_WAR_BOAR"],
        ),
    )

    captain_chariot = ConfiguredProfile(
        profile=profiles["IH_CAP"],
        selected_options=(
            options["IH_CAP_CHARIOT"],
        ),
    )

    captain_mattock = ConfiguredProfile(
        profile=profiles["IH_CAP"],
        selected_options=(
            options["IH_CAP_MATTOCK"],
        ),
    )

    goat_rider = ConfiguredProfile(
        profile=profiles["IH_GR"],
    )

    goat_rider_mattock = ConfiguredProfile(
        profile=profiles["IH_GR"],
        selected_options=(
            options["IH_GR_MATTOCK"],
        ),
    )

    assert dain.points == 185
    assert dain.effective_mount is (
        mounts["MOUNT_WAR_BOAR"]
    )
    assert dain.effective_platform is None

    assert captain_chariot.points == 250
    assert captain_chariot.effective_platform is (
        platforms["PLATFORM_IRON_HILLS_CHARIOT"]
    )
    assert captain_chariot.effective_mount is None

    assert captain_mattock.points == 80
    assert {
        item.id
        for item in captain_mattock.effective_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_MATTOCK",
    }

    assert goat_rider.points == 20
    assert goat_rider.effective_mount is (
        mounts["MOUNT_IRON_HILLS_GOAT"]
    )
    assert {
        item.id
        for item in goat_rider.effective_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_WAR_SPEAR",
        "WG_HAND_WEAPON",
    }

    assert goat_rider_mattock.points == 20
    assert goat_rider_mattock.effective_mount is (
        mounts["MOUNT_IRON_HILLS_GOAT"]
    )
    assert {
        item.id
        for item in goat_rider_mattock.effective_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_MATTOCK",
    }