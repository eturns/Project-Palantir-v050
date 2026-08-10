from army_definition import ArmyEntryDefinition
from importers.mesbg_list_builder_json_importer import (
    build_configured_army_entry_definitions,
)
from mapped_configured_entry import (
    MappedConfiguredEntry,
)


def test_build_configured_army_entry_definitions():
    entries = [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=2,
        )
    ]

    definitions = (
        build_configured_army_entry_definitions(
            entries
        )
    )

    assert definitions == [
        ArmyEntryDefinition(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=2,
        )
    ]


def test_build_configured_definitions_preserves_distinct_options():
    entries = [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0723",),
            quantity=3,
        ),
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=2,
        ),
    ]

    definitions = (
        build_configured_army_entry_definitions(
            entries
        )
    )

    assert len(definitions) == 2

    assert definitions[0].external_option_ids == (
        "OPT0723",
    )
    assert definitions[0].quantity == 3

    assert definitions[1].external_option_ids == (
        "OPT0724",
    )
    assert definitions[1].quantity == 2


def test_build_configured_army_entry_definitions_handles_empty_list():
    assert build_configured_army_entry_definitions(
        []
    ) == []