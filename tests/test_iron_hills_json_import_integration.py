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