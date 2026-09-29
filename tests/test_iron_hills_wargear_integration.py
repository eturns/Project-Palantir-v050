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
from loader import load_all_profiles
from profile_metrics import calculate_profile_metrics

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
        for loaded_profile in load_all_profiles()
    }

    profiles["IH_WR"] = profile

    wargear = load_wargear()

    options = load_profile_options(
        profiles=profiles,
        skip_unknown_profiles=True,
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
        for profile in load_all_profiles()
    }

    wargear = load_wargear()

    options = load_profile_options(
        profiles=profiles,
        skip_unknown_profiles=True,
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
            for profile in load_all_profiles()
        }

    wargear = load_wargear()

    options = load_profile_options(
        profiles=profiles,
        skip_unknown_profiles=True,
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

def test_iron_hills_crossbow_contributes_to_shooting_metric():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    wargear = load_wargear()

    options = load_profile_options(
        profiles=profiles,
        skip_unknown_profiles=True,
    )

    load_profile_default_wargear(
        profiles=profiles,
        wargear=wargear,
    )

    load_profile_option_wargear_assignments(
        profile_options=options,
        wargear=wargear,
    )

    warrior = profiles["IH_WR"]

    without_crossbow = ConfiguredProfile(
        profile=warrior,
    )

    with_crossbow = ConfiguredProfile(
        profile=warrior,
        selected_options=(
            options["IH_WR_CROSSBOW"],
        ),
    )

    assert (
        calculate_profile_metrics(with_crossbow).shooting
        > calculate_profile_metrics(without_crossbow).shooting
    )

def test_ranged_wargear_metric_uses_effective_equipment():
    from profile_metrics import calculate_ranged_wargear_metric
    from profile_option import ProfileOption
    from profile_option_wargear_assignment import (
        ProfileOptionWargearAssignment,
        WargearAssignmentAction,
    )

    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }
    warrior = profiles["IH_WR"]
    crossbow = load_wargear()["WG_CROSSBOW"]

    # Set up a profile that starts with a Crossbow.
    warrior.default_wargear.append(crossbow)

    remove_crossbow = ProfileOption(
        id="TEST_REMOVE_CROSSBOW",
        name="Remove Crossbow",
        points=0,
        wargear_assignments=(
            ProfileOptionWargearAssignment(
                wargear=crossbow,
                action=WargearAssignmentAction.REMOVE,
            ),
        ),
    )
    warrior.profile_options.append(remove_crossbow)

    equipped = ConfiguredProfile(profile=warrior)
    unequipped = ConfiguredProfile(
        profile=warrior,
        selected_options=(remove_crossbow,),
    )

    assert calculate_ranged_wargear_metric(equipped) == 1.0
    assert calculate_ranged_wargear_metric(unequipped) == 0.0