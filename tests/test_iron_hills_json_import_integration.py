import json

from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
)
from configured_profile import ConfiguredProfile
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)
from profile_option_loader import load_profile_options
from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
    get_palantir_army_list_id,
)
from loader import load_all_profiles
from army_loader import (
    load_factions,
    load_army_lists,
    load_army_list_profiles,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from profile_option_loader import (
    build_profile_options_by_external_id,
)
from mount_loader import load_mounts
from profile_option_mount_loader import (
    load_profile_option_mount_assignments,
)
from wargear_loader import load_wargear
from profile_option_wargear_loader import (
    load_profile_option_wargear_assignments,
)
from model_platform_loader import load_platforms
from profile_option_platform_loader import (
    load_profile_option_platform_assignments,
)
from profile_option_state_effect_loader import (
    load_profile_option_state_effects,
)

from analysis_loader import load_metric_thresholds
from services.mesbg_list_analysis_service import (
    analyse_mesbg_list_builder_file,
)

def load_production_profiles_and_options():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    profile_options = load_profile_options(
        profiles_by_id,
    )

    mounts = load_mounts()

    load_profile_option_mount_assignments(
        profile_options,
        mounts,
    )

    wargear = load_wargear()

    load_profile_option_wargear_assignments(
        profile_options,
        wargear,
    )

    platforms = load_platforms()

    load_profile_option_platform_assignments(
        profile_options,
        platforms,
    )

    load_profile_option_state_effects(
        profile_options,
    )

    profile_options_by_external_id = (
        build_profile_options_by_external_id(
            profile_options
        )
    )

    return (
        profiles_by_id,
        profile_options_by_external_id,
    )

def get_entry(
    army_definition,
    profile_id: str,
    external_option_ids: tuple[str, ...] = (),
):
    return next(
        entry
        for entry in army_definition.entries
        if (
            entry.profile_id == profile_id
            and entry.external_option_ids
            == external_option_ids
        )
    )

def load_iron_hills_json() -> dict:
    with open(
        "tests/fixtures/iron_hills_army.json",
        encoding="utf-8",
    ) as json_file:
        return json.load(json_file)


def test_imports_real_iron_hills_army_identity():
    data = load_iron_hills_json()

    army_definition = build_army_definition_from_data(
        data,
    )

    assert army_definition.army_list_id == (
        "IH_IRON_HILLS"
    )
def load_profiles_and_options():
    profiles = {
        profile.id: profile
        for profile in load_iron_hills_test_profiles()
    }

    options = load_profile_options(
        profiles=profiles,
        skip_unknown_profiles=True,
    )

    options_by_external_id = {
        option.external_id: option
        for option in options.values()
    }

    return profiles, options_by_external_id

def test_real_iron_hills_import_has_no_points_limit():
    data = load_iron_hills_json()

    army_definition = build_army_definition_from_data(
        data,
    )

    assert army_definition.points_limit is None


def test_real_iron_hills_import_creates_entries():
    data = load_iron_hills_json()

    army_definition = build_army_definition_from_data(
        data,
    )

    assert army_definition.entries

def test_real_iron_hills_import_maps_dain_on_war_boar():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    entry = get_entry(
        army_definition,
        "IH_DAIN",
        ("OPT0718",),
    )

    assert entry.quantity == 1


def test_real_iron_hills_import_maps_captain_on_chariot():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    entry = get_entry(
        army_definition,
        "IH_CAP",
        ("OPT0719",),
    )

    assert entry.quantity == 1


def test_real_iron_hills_import_maps_goat_rider_mattock():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    entry = get_entry(
        army_definition,
        "IH_GR",
        ("OPT0726",),
    )

    assert entry.quantity == 1


def test_real_iron_hills_import_keeps_two_crossbows_grouped():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    entry = get_entry(
        army_definition,
        "IH_WR",
        ("OPT0724",),
    )

    assert entry.quantity == 2

def test_real_iron_hills_import_keeps_warrior_configurations_distinct():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    warrior_entries = [
        entry
        for entry in army_definition.entries
        if entry.profile_id == "IH_WR"
    ]

    configurations = {
        entry.external_option_ids: entry.quantity
        for entry in warrior_entries
    }

    assert configurations[("OPT0721",)] == 1
    assert configurations[("OPT0723",)] == 1
    assert configurations[("OPT0724",)] == 2
    assert configurations[("OPT0725",)] == 1

def test_real_iron_hills_import_keeps_captain_configurations_distinct():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    captain_entries = [
        entry
        for entry in army_definition.entries
        if entry.profile_id == "IH_CAP"
    ]

    configurations = {
        entry.external_option_ids: entry.quantity
        for entry in captain_entries
    }

    assert configurations[("OPT0719",)] == 1
    assert configurations[("OPT0720",)] == 1

def test_real_iron_hills_import_resolves_configured_points():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    profiles, options_by_external_id = (
        load_profiles_and_options()
    )

    configured_points_by_entry = {}

    for entry in army_definition.entries:
        selected_options = tuple(
            options_by_external_id[external_id]
            for external_id
            in entry.external_option_ids
        )

        configured_profile = ConfiguredProfile(
            profile=profiles[entry.profile_id],
            selected_options=selected_options,
        )

        configured_points_by_entry[
            (
                entry.profile_id,
                entry.external_option_ids,
            )
        ] = configured_profile.points

    assert configured_points_by_entry[
        ("IH_DAIN", ("OPT0718",))
    ] == 185

    assert configured_points_by_entry[
        ("IH_CAP", ("OPT0719",))
    ] == 250

    assert configured_points_by_entry[
        ("IH_CAP", ("OPT0720",))
    ] == 80

    assert configured_points_by_entry[
        ("IH_GR", ("OPT0726",))
    ] == 20

    assert configured_points_by_entry[
        ("IH_WR", ("OPT0721",))
    ] == 36

    assert configured_points_by_entry[
        ("IH_WR", ("OPT0723",))
    ] == 12

    assert configured_points_by_entry[
        ("IH_WR", ("OPT0724",))
    ] == 12

    assert configured_points_by_entry[
        ("IH_WR", ("OPT0725",))
    ] == 11

def test_real_iron_hills_import_reproduces_total_points():
    army_definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    profiles, options_by_external_id = (
        load_profiles_and_options()
    )

    total_points = 0

    for entry in army_definition.entries:
        selected_options = tuple(
            options_by_external_id[external_id]
            for external_id
            in entry.external_option_ids
        )

        configured_profile = ConfiguredProfile(
            profile=profiles[entry.profile_id],
            selected_options=selected_options,
        )

        total_points += (
            configured_profile.points
            * entry.quantity
        )

    assert total_points == 823

def test_get_palantir_army_list_id_maps_the_iron_hills():
    data = {
        "armyList": "The Iron Hills",
    }

    assert get_palantir_army_list_id(
        data
    ) == "IH_IRON_HILLS"

def test_real_iron_hills_json_builds_configured_runtime_army():
    (
        profiles_by_id,
        profile_options_by_external_id,
    ) = load_production_profiles_and_options()

    factions = load_factions()

    army_lists = load_army_lists(
        factions
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    definition, army, army_list = (
        import_army_from_mesbg_list_builder(
            "tests/fixtures/iron_hills_army.json",
            profiles_by_id,
            army_lists,
            profile_options_by_external_id=(
                profile_options_by_external_id
            ),
        )
    )

    assert definition.army_list_id == (
        "IH_IRON_HILLS"
    )

    assert definition.points_limit is None

    assert army_list.id == (
        "IH_IRON_HILLS"
    )

    assert army.total_points() == 823

    assert army.model_count() == 11

    configured_entries = {
        (
            entry.profile.id,
            tuple(
                option.external_id
                for option
                in entry.configured_profile.selected_options
            ),
        ): entry
        for entry in army.entries
    }

    def wargear_ids(entry):
        return {
            item.id
            for item in (
                entry
                .configured_profile
                .effective_wargear
            )
        }


    assert wargear_ids(
        configured_entries[
            ("IH_WR", ("OPT0721",))
        ]
    ) >= {
        "WG_BANNER",
        "WG_SHIELD",
    }

    assert wargear_ids(
        configured_entries[
            ("IH_WR", ("OPT0723",))
        ]
    ) >= {
        "WG_SHIELD",
        "WG_SPEAR",
    }

    assert wargear_ids(
        configured_entries[
            ("IH_WR", ("OPT0724",))
        ]
    ) >= {
        "WG_CROSSBOW",
    }

    assert wargear_ids(
        configured_entries[
            ("IH_CAP", ("OPT0720",))
        ]
    ) >= {
        "WG_MATTOCK",
    }

    assert "WG_SHIELD" not in wargear_ids(
        configured_entries[
            ("IH_CAP", ("OPT0720",))
        ]
    )

    assert "WG_SPEAR" not in wargear_ids(
        configured_entries[
            ("IH_CAP", ("OPT0720",))
        ]
    )

    assert wargear_ids(
        configured_entries[
            ("IH_GR", ("OPT0726",))
        ]
    ) >= {
        "WG_MATTOCK",
    }

    assert "WG_WAR_SPEAR" not in wargear_ids(
        configured_entries[
            ("IH_GR", ("OPT0726",))
        ]
    )

    assert (
        configured_entries[
            ("IH_DAIN", ("OPT0718",))
        ].configured_profile.effective_mount.id
        == "MOUNT_WAR_BOAR"
    )

    assert (
        configured_entries[
            ("IH_DAIN", ("OPT0718",))
        ].configured_profile.effective_base_size_mm
        == 40
    )

    assert (
        configured_entries[
            ("IH_DAIN", ("OPT0718",))
        ].configured_profile.points
        == 185
    )

    assert (
        configured_entries[
            ("IH_CAP", ("OPT0719",))
        ].configured_profile.points
        == 250
    )

    assert (
        configured_entries[
            ("IH_CAP", ("OPT0720",))
        ].configured_profile.points
        == 80
    )

    assert (
        configured_entries[
            ("IH_GR", ("OPT0726",))
        ].configured_profile.points
        == 20
    )

    assert (
        configured_entries[
            ("IH_WR", ("OPT0721",))
        ].configured_profile.points
        == 36
    )

    assert (
        configured_entries[
            ("IH_WR", ("OPT0723",))
        ].configured_profile.points
        == 12
    )

    assert (
        configured_entries[
            ("IH_WR", ("OPT0724",))
        ].quantity
        == 2
    )

    assert (
        configured_entries[
            ("IH_WR", ("OPT0724",))
        ].configured_profile.points
        == 12
    )

    assert (
        configured_entries[
            ("IH_WR", ("OPT0725",))
        ].configured_profile.points
        == 11
    )

    fielded_models = army.fielded_models()

    assert len(fielded_models) == 11

    assert len({
        model.id
        for model in fielded_models
    }) == 11

def test_real_iron_hills_json_runs_shared_analysis_path():
    (
        profiles_by_id,
        profile_options_by_external_id,
    ) = load_production_profiles_and_options()

    factions = load_factions()

    army_lists = load_army_lists(
        factions
    )

    load_army_list_profiles(
        army_lists=army_lists,
        profiles_by_id=profiles_by_id,
    )

    metric_thresholds = (
        load_metric_thresholds()
    )

    result = analyse_mesbg_list_builder_file(
        "tests/fixtures/iron_hills_army.json",
        profiles_by_id,
        army_lists,
        metric_thresholds,
        profile_options_by_external_id=(
            profile_options_by_external_id
        ),
    )

    assert result["definition"].army_list_id == (
        "IH_IRON_HILLS"
    )

    assert result["definition"].points_limit is None

    assert result["army_list"].id == (
        "IH_IRON_HILLS"
    )

    assert result["army"].total_points() == 823

    assert result["army"].model_count() == 11

    assert result["analysis"] is not None

    assert (
        result["analysis"]["validation_errors"]
        == []
    )

    assert (
        result["scenario_analysis_results"]
        is not None
    )