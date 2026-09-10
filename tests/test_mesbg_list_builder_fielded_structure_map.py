from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from importers.mesbg_list_builder_fielded_structure_map import (
    FIELDED_MODEL_STRUCTURE_DEFINITIONS,
    IMPORTED_FIELDED_STRUCTURE_DEFINITIONS,
)


def test_mumak_import_structure_definition_exists():
    definition = (
        IMPORTED_FIELDED_STRUCTURE_DEFINITIONS[
            "[usurpers-of-edoras] war-mumak-of-harad"
        ]
    )

    assert definition.root_profile_id == "WAR_MUMAK"

    assert definition.member_profile_ids == (
        "HARADRIM_COMMANDER",
    )


def test_mumak_fielded_structure_definition_exists():
    definition = (
        FIELDED_MODEL_STRUCTURE_DEFINITIONS[
            "WAR_MUMAK"
        ]
    )

    assert (
        definition.members[0].profile_id
        == "HARADRIM_COMMANDER"
    )

    assert (
        definition.members[0].relationship_type
        == FieldedModelRelationshipType
        .WAR_BEAST_COMMANDER_OF
    )

    assert (
        definition.warband_member_relationship_type
        == FieldedModelRelationshipType
        .HOWDAH_OCCUPANT_OF
    )