import json

from army_definition import ArmyEntryDefinition
from importers.mesbg_list_builder_json_importer import (
    build_configured_army_entry_definitions,
    build_configured_army_entry_definitions_from_data,
    build_army_definition_from_data,
    import_army_definition_from_json,
)
from mapped_configured_entry import (
    MappedConfiguredEntry,
)
from imported_fielded_structure_definition import (
    ImportedFieldedStructureDefinition,
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

def test_build_configured_army_entry_definitions_preserves_warband_id():
    entries = [
        MappedConfiguredEntry(
            profile_id="IH_WR",
            external_option_ids=("OPT0724",),
            quantity=2,
            warband_id="WARBAND_A",
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
            warband_id="WARBAND_A",
        )
    ]

def test_build_configured_definitions_expands_structure():
    data = {
        "warbands": [
            {
                "id": "WARBAND_A",
                "hero": {
                    "model_id": "EXT_MUMAK",
                    "options": [],
                },
                "units": [],
            },
        ],
    }

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_MUMAK",
            root_profile_id="WAR_MUMAK",
            member_profile_ids=(
                "HARADRIM_COMMANDER",
            ),
        )
    )

    definitions = (
        build_configured_army_entry_definitions_from_data(
            data,
            structure_definitions={
                "EXT_MUMAK": structure_definition,
            },
        )
    )

    assert len(definitions) == 2

    assert definitions[0].profile_id == (
        "HARADRIM_COMMANDER"
    )
    assert definitions[0].warband_id == (
        "WARBAND_A"
    )

    assert definitions[1].profile_id == (
        "WAR_MUMAK"
    )
    assert definitions[1].warband_id == (
        "WARBAND_A"
    )

def test_build_army_definition_expands_structure():
    data = {
        "id": "TEST_ARMY",
        "name": "Test Army",
        "armyList": "The Iron Hills",
        "metadata": {
            "maxPoints": 700,
            "leader": "WARBAND_A",
        },
        "warbands": [
            {
                "id": "WARBAND_A",
                "hero": {
                    "model_id": "EXT_MUMAK",
                    "options": [],
                },
                "units": [],
            },
        ],
    }

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_MUMAK",
            root_profile_id="WAR_MUMAK",
            member_profile_ids=(
                "HARADRIM_COMMANDER",
            ),
        )
    )

    definition = build_army_definition_from_data(
        data,
        structure_definitions={
            "EXT_MUMAK": structure_definition,
        },
    )

    assert definition.leader_profile_id == (
        "WAR_MUMAK"
    )

    assert len(definition.entries) == 2

    assert tuple(
        entry.profile_id
        for entry in definition.entries
    ) == (
        "HARADRIM_COMMANDER",
        "WAR_MUMAK",
    )

    assert tuple(
        entry.warband_id
        for entry in definition.entries
    ) == (
        "WARBAND_A",
        "WARBAND_A",
    )

def test_import_army_definition_from_json_expands_structure(
    tmp_path,
):
    data = {
        "id": "TEST_ARMY",
        "name": "Test Army",
        "armyList": "The Iron Hills",
        "metadata": {
            "maxPoints": 700,
            "leader": "WARBAND_A",
        },
        "warbands": [
            {
                "id": "WARBAND_A",
                "hero": {
                    "model_id": "EXT_MUMAK",
                    "options": [],
                },
                "units": [],
            },
        ],
    }

    file_path = tmp_path / "test_army.json"

    file_path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    structure_definition = (
        ImportedFieldedStructureDefinition(
            external_model_id="EXT_MUMAK",
            root_profile_id="WAR_MUMAK",
            member_profile_ids=(
                "HARADRIM_COMMANDER",
            ),
        )
    )

    definition = import_army_definition_from_json(
        str(file_path),
        structure_definitions={
            "EXT_MUMAK": structure_definition,
        },
    )

    assert tuple(
        entry.profile_id
        for entry in definition.entries
    ) == (
        "HARADRIM_COMMANDER",
        "WAR_MUMAK",
    )

    assert definition.leader_profile_id == (
        "WAR_MUMAK"
    )

def test_build_army_definition_uses_default_mumak_structure():
    data = {
        "id": "TEST_ARMY",
        "name": "Test Army",
        "armyList": "The Iron Hills",
        "metadata": {
            "maxPoints": 700,
            "leader": "WARBAND_A",
        },
        "warbands": [
            {
                "id": "WARBAND_A",
                "hero": {
                    "model_id": (
                        "[usurpers-of-edoras] "
                        "war-mumak-of-harad"
                    ),
                    "options": [],
                },
                "units": [],
            },
        ],
    }

    definition = build_army_definition_from_data(
        data,
    )

    assert tuple(
        entry.profile_id
        for entry in definition.entries
    ) == (
        "HARADRIM_COMMANDER",
        "WAR_MUMAK",
    )

    assert definition.leader_profile_id == (
        "WAR_MUMAK"
    )