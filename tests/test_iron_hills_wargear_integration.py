from configured_profile import ConfiguredProfile
from profile_default_wargear_loader import (
    load_profile_default_wargear,
)
from profile_option_loader import load_profile_options
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from profiles import Profile
from wargear_loader import load_wargear
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)

def create_iron_hills_warrior() -> Profile:
    return Profile(
        id="IH_WR",
        name="Iron Hills Warrior",
        points=10,
        movement=5,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
        courage="6+",
        intelligence="6+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
    )


def test_iron_hills_warrior_shield_and_spear_configuration():
    profile = create_iron_hills_warrior()

    profiles = {
        loaded_profile.id: loaded_profile
        for loaded_profile
        in load_iron_hills_test_profiles()
    }

    profiles["IH_WR"] = profile

    wargear = load_wargear()

    options = load_profile_options(
        profiles=profiles,
    )

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    load_profile_option_wargear_assignments(
        profile_options=options,
        wargear=wargear,
    )

    configured_profile = ConfiguredProfile(
        profile=profile,
        selected_options=(
            options["IH_WR_SHIELD_SPEAR"],
        ),
    )

    assert configured_profile.points == 12

    assert tuple(
        item.id
        for item in configured_profile.effective_wargear
    ) == (
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_SHIELD",
        "WG_SPEAR",
    )

def test_iron_hills_captain_mattock_configuration():
    profiles = {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }

    wargear = load_wargear()

    options = load_profile_options(
        profiles=profiles,
    )

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    load_profile_option_wargear_assignments(
        profile_options=options,
        wargear=wargear,
    )

    configured_profile = ConfiguredProfile(
        profile=profiles["IH_CAP"],
        selected_options=(
            options["IH_CAP_MATTOCK"],
        ),
    )

    assert {
        item.id
        for item in configured_profile.effective_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_MATTOCK",
    }


def test_iron_hills_goat_rider_mattock_configuration():
    profiles = {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }

    wargear = load_wargear()

    options = load_profile_options(
        profiles=profiles,
    )

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    load_profile_option_wargear_assignments(
        profile_options=options,
        wargear=wargear,
    )

    configured_profile = ConfiguredProfile(
        profile=profiles["IH_GR"],
        selected_options=(
            options["IH_GR_MATTOCK"],
        ),
    )

    assert {
        item.id
        for item in configured_profile.effective_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_MATTOCK",
    }