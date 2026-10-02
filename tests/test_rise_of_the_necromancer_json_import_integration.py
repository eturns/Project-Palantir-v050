from importers.mesbg_list_builder_json_importer import (
    import_army_definition_from_json,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from loader import load_all_profiles
from army_loader import (
    load_army_list_profiles,
    load_army_lists,
    load_factions,
)
from profile_option_loader import (
    build_profile_options_by_external_id,
    load_profile_options,
)
from mount_loader import load_mounts
from profile_default_mount_loader import (
    load_profile_default_mounts,
)
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from wargear_loader import load_wargear
from profile_default_wargear_loader import (
    load_profile_default_wargear,
)
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)


FIXTURE_PATH = (
    "tests/fixtures/"
    "rise_of_the_necromancer_all_options.json"
)


def load_production_rise_data():
    profiles_by_id = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    wargear = load_wargear()
    mounts = load_mounts()

    profile_options = load_profile_options(
        profiles=profiles_by_id,
    )

    load_profile_default_wargear(
        profiles=profiles_by_id,
        wargear=wargear,
    )

    load_profile_default_mounts(
        profiles=profiles_by_id,
        mounts=mounts,
    )

    load_profile_option_wargear_assignments(
        profile_options=profile_options,
        wargear=wargear,
    )

    load_profile_option_mount_assignments(
        profile_options=profile_options,
        mounts=mounts,
    )

    load_profile_option_state_effects(
        profile_options=profile_options,
    )

    options_by_external_id = (
        build_profile_options_by_external_id(
            profile_options
        )
    )

    factions = load_factions()

    army_lists = load_army_lists(
        factions,
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    return (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    )


def test_real_rise_json_maps_complete_profile_set():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    assert definition.army_list_id == "DG_ROTN"
    assert definition.points_limit is None
    assert definition.leader_profile_id == "DG_NEC"

    assert {
        entry.profile_id
        for entry in definition.entries
    } == {
        "DG_NEC",
        "DG_WK",
        "DG_KHM",
        "DG_DH",
        "DG_FS",
        "DG_LS",
        "DG_AK",
        "DG_SM",
        "DG_KEEPER",
        "DG_HOC",
        "DG_HOW",
        "DG_HOWR",
        "DG_FW",
        "DG_MGS",
        "DG_MHS",
        "DG_CASTELLAN",
    }


def test_real_rise_json_preserves_all_seven_options():
    definition = import_army_definition_from_json(
        FIXTURE_PATH,
    )

    external_option_ids = {
        option_id
        for entry in definition.entries
        for option_id in entry.external_option_ids
    }

    assert external_option_ids == {
        "OPT0702",
        "OPT0703",
        "OPT0704",
        "OPT0705",
        "OPT0706",
        "OPT0707",
        "OPT0708",
    }


def test_real_rise_json_builds_complete_runtime_army():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_rise_data()

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            FIXTURE_PATH,
            profiles_by_id=profiles_by_id,
            army_lists_by_id=army_lists,
            profile_options_by_external_id=(
                options_by_external_id
            ),
        )
    )

    assert definition.army_list_id == "DG_ROTN"
    assert army_list.id == "DG_ROTN"

    assert army.total_points() == 1291
    assert army.model_count() == 24


def test_real_rise_json_resolves_configured_hunter_orcs():
    (
        profiles_by_id,
        army_lists,
        options_by_external_id,
    ) = load_production_rise_data()

    _, army, _ = import_army_from_mesbg_list_builder(
        FIXTURE_PATH,
        profiles_by_id=profiles_by_id,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    configured_models = tuple(
        model
        for model in army.fielded_models()
        if model.configured_profile is not None
    )

    mounted_bow_captain = next(
        model.configured_profile
        for model in configured_models
        if (
            model.profile_id == "DG_HOC"
            and {
                option.external_id
                for option
                in model.configured_profile.selected_options
            }
            == {
                "OPT0702",
                "OPT0703",
            }
        )
    )

    assert mounted_bow_captain.points == 70
    assert mounted_bow_captain.effective_movement == 10
    assert mounted_bow_captain.effective_base_size_mm == 40

    assert (
        mounted_bow_captain.effective_mount.id
        == "MOUNT_FELL_WARG"
    )

    assert "WG_ORC_BOW" in {
        item.id
        for item in mounted_bow_captain.effective_wargear
    }

    warg_riders = tuple(
        model.configured_profile
        for model in configured_models
        if model.profile_id == "DG_HOWR"
    )

    assert len(warg_riders) == 3

    assert all(
        rider.effective_mount.id
        == "MOUNT_FELL_WARG"
        for rider in warg_riders
    )