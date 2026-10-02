from configured_profile import ConfiguredProfile
from loader import load_all_profiles
from mount_loader import load_mounts
from profile_classification import ModelType
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
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from wargear_loader import load_wargear


def load_rise_configuration():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    wargear = load_wargear()
    mounts = load_mounts()

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

    load_profile_option_state_effects(
        profile_options=options,
    )

    return profiles, options, mounts


def test_existing_rise_profiles_have_default_wargear():
    profiles, _, _ = load_rise_configuration()

    necromancer = ConfiguredProfile(
        profile=profiles["DG_NEC"],
    )

    abyssal_knight = ConfiguredProfile(
        profile=profiles["DG_AK"],
    )

    assert {
        item.id
        for item in necromancer.effective_wargear
    } == {
        "WG_SPECTRAL_HANDS",
    }

    assert {
        item.id
        for item in abyssal_knight.effective_wargear
    } == {
        "WG_ARMOUR",
        "WG_ELVEN_HAND_AND_A_HALF_WEAPON",
    }


def test_new_rise_profiles_have_default_wargear():
    profiles, _, _ = load_rise_configuration()

    keeper = ConfiguredProfile(
        profile=profiles["DG_KEEPER"],
    )

    castellan = ConfiguredProfile(
        profile=profiles["DG_CASTELLAN"],
    )

    assert {
        item.id
        for item in keeper.effective_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_TWO_HANDED_WEAPON",
    }

    assert {
        item.id
        for item in castellan.effective_wargear
    } == {
        "WG_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_MORGUL_BLADE",
    }


def test_hunter_orc_captain_fell_warg_configuration():
    profiles, options, mounts = load_rise_configuration()

    configured = ConfiguredProfile(
        profile=profiles["DG_HOC"],
        selected_options=(
            options["DG_HOC_FELL_WARG"],
        ),
    )

    assert configured.points == 65

    assert configured.effective_mount is mounts[
        "MOUNT_FELL_WARG"
    ]

    assert configured.effective_movement == 10
    assert configured.effective_base_size_mm == 40

    assert configured.effective_model_types == {
        ModelType.CAVALRY,
    }


def test_hunter_orc_warg_rider_has_inherent_fell_warg():
    profiles, _, mounts = load_rise_configuration()

    configured = ConfiguredProfile(
        profile=profiles["DG_HOWR"],
    )

    assert configured.points == 15

    assert configured.effective_mount is mounts[
        "MOUNT_FELL_WARG"
    ]

    assert configured.effective_movement == 10
    assert configured.effective_fight == 3
    assert configured.effective_strength == 4
    assert configured.effective_attacks == 1
    assert configured.effective_base_size_mm == 40

    assert configured.effective_model_types == {
        ModelType.CAVALRY,
    }

def test_hunter_orc_captain_fell_warg_configuration():
    profiles, options, mounts = load_rise_configuration()

    configured = ConfiguredProfile(
        profile=profiles["DG_HOC"],
        selected_options=(
            options["DG_HOC_FELL_WARG"],
        ),
    )

    assert configured.points == 65

    assert configured.effective_mount is mounts[
        "MOUNT_FELL_WARG"
    ]

    assert configured.effective_movement == 10
    assert configured.effective_fight == 4
    assert configured.effective_strength == 4
    assert configured.effective_attacks == 2
    assert configured.effective_base_size_mm == 40

    assert configured.effective_model_types == {
        ModelType.CAVALRY,
    }


def test_all_rise_external_options_load():
    _, options, _ = load_rise_configuration()

    expected_external_ids = {
        "OPT0702",
        "OPT0703",
        "OPT0704",
        "OPT0705",
        "OPT0706",
        "OPT0707",
        "OPT0708",
    }

    actual_external_ids = {
        option.external_id
        for option in options.values()
        if option.external_id in expected_external_ids
    }

    assert actual_external_ids == expected_external_ids