from army_builder import build_army_from_definition
from importers.mesbg_list_builder_json_importer import (
    build_army_definition_from_data,
)

from test_iron_hills_json_import_integration import (
    load_iron_hills_json,
    load_profiles_and_options,
)
from configured_state_effect import ConfiguredStateEffect

def test_dev061_import_to_army_preserves_distinct_configurations():
    definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    profiles_by_id, options_by_external_id = (
        load_profiles_and_options()
    )

    army_lists_by_id = {
        definition.army_list_id: object(),
    }

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id,
        army_lists_by_id,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    warrior_entries = [
        entry
        for entry in army.entries
        if entry.profile.id == "IH_WR"
    ]

    assert len(warrior_entries) == 5

    assert all(
        entry.profile
        is warrior_entries[0].profile
        for entry in warrior_entries
    )

    configurations = {
        tuple(
            option.external_id
            for option
            in entry.configured_profile.selected_options
        ): entry.quantity
        for entry in warrior_entries
    }

    assert configurations[
        ("OPT0721",)
    ] == 1

    assert configurations[
        ("OPT0722",)
    ] == 1

    assert configurations[
        ("OPT0723",)
    ] == 1

    assert configurations[
        ("OPT0724",)
    ] == 2

    assert configurations[
        ("OPT0725",)
    ] == 1

def test_dev061_imported_configuration_preserves_effective_defence():
    definition = build_army_definition_from_data(
        load_iron_hills_json(),
    )

    profiles_by_id, options_by_external_id = (
        load_profiles_and_options()
    )

    shield_and_spear_option = (
        options_by_external_id["OPT0723"]
    )

    object.__setattr__(
        shield_and_spear_option,
        "configured_state_effects",
        (
            ConfiguredStateEffect(
                defence_modifier=1,
            ),
        ),
    )

    army_lists_by_id = {
        definition.army_list_id: object(),
    }

    army, _ = build_army_from_definition(
        definition,
        profiles_by_id,
        army_lists_by_id,
        profile_options_by_external_id=(
            options_by_external_id
        ),
    )

    shield_and_spear_entry = next(
        entry
        for entry in army.entries
        if (
            entry.profile.id == "IH_WR"
            and tuple(
                option.external_id
                for option
                in entry.configured_profile.selected_options
            )
            == ("OPT0723",)
        )
    )

    assert (
        shield_and_spear_entry.profile.defence
        == 6
    )

    assert (
        shield_and_spear_entry.configured_profile.effective_defence
        == 7
    )

    assert (
        shield_and_spear_entry.get_attribute(
            "defence"
        )
        == 7
    )