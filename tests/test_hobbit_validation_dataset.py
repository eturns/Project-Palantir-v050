from configured_profile import ConfiguredProfile
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)
from loader import load_all_profiles
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


def load_validation_dataset():
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

    return profiles, options

def test_validation_dataset_contains_required_profile_cases():
    profiles, options = load_validation_dataset()

    basic_infantry = ConfiguredProfile(
        profile=profiles["IH_WR"],
        selected_options=(),
    )

    hero = ConfiguredProfile(
        profile=profiles["IH_CAP"],
        selected_options=(),
    )

    support_model = ConfiguredProfile(
        profile=profiles["IH_WR"],
        selected_options=(
            options["IH_WR_SHIELD_SPEAR"],
        ),
    )

    banner_model = ConfiguredProfile(
        profile=profiles["IH_WR"],
        selected_options=(
            options["IH_WR_BANNER"],
        ),
    )

    cavalry_model = ConfiguredProfile(
        profile=profiles["IH_GR"],
        selected_options=(),
    )

    optional_mount_model = ConfiguredProfile(
        profile=profiles["IH_DAIN"],
        selected_options=(
            options["IH_DAIN_WAR_BOAR"],
        ),
    )

    platform_model = ConfiguredProfile(
        profile=profiles["IH_CAP"],
        selected_options=(
            options["IH_CAP_CHARIOT"],
        ),
    )

    assert basic_infantry.profile.id == "IH_WR"
    assert hero.profile.id == "IH_CAP"

    assert {
        item.id
        for item in support_model.effective_wargear
    } >= {
        "WG_SPEAR",
        "WG_SHIELD",
    }

    assert "WG_BANNER" in {
        item.id
        for item in banner_model.effective_wargear
    }

    assert cavalry_model.effective_mount is not None
    assert optional_mount_model.effective_mount is not None
    assert platform_model.effective_platform is not None

def test_validation_dataset_spans_multiple_factions():
    dol_guldur_profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    iron_hills_profiles, _ = load_validation_dataset()

    required_profile_ids = {
        "DG_NEC",
        "IH_WR",
        "IH_CAP",
        "IH_DAIN",
        "IH_GR",
        "IH_CHARIOT",
    }

    loaded_profile_ids = (
        set(dol_guldur_profiles)
        | set(iron_hills_profiles)
    )

    assert required_profile_ids <= loaded_profile_ids