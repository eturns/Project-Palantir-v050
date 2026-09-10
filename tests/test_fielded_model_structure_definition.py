import pytest

from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_structure_definition import (
    FieldedModelStructureDefinition,
)
from fielded_model_structure_member import (
    FieldedModelStructureMember,
)


def make_member() -> FieldedModelStructureMember:
    return FieldedModelStructureMember(
        profile_id="COMMANDER",
        relationship_type=(
            FieldedModelRelationshipType
            .WAR_BEAST_COMMANDER_OF
        ),
    )


def test_structure_definition_preserves_values():
    member = make_member()

    definition = FieldedModelStructureDefinition(
        root_profile_id="WAR_MUMAK",
        members=(member,),
    )

    assert definition.root_profile_id == "WAR_MUMAK"
    assert definition.members == (member,)


def test_structure_definition_rejects_empty_root_profile_id():
    with pytest.raises(
        ValueError,
        match="Structure root profile id",
    ):
        FieldedModelStructureDefinition(
            root_profile_id="",
            members=(make_member(),),
        )


def test_structure_definition_rejects_empty_members():
    with pytest.raises(
        ValueError,
        match=(
            "Structure definition must contain "
            "at least one member"
        ),
    ):
        FieldedModelStructureDefinition(
            root_profile_id="WAR_MUMAK",
            members=(),
        )

def test_structure_definition_preserves_warband_relationship_type():
    definition = FieldedModelStructureDefinition(
        root_profile_id="WAR_MUMAK",
        members=(make_member(),),
        warband_member_relationship_type=(
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        ),
    )

    assert (
        definition.warband_member_relationship_type
        is FieldedModelRelationshipType
        .HOWDAH_OCCUPANT_OF
    )


def test_structure_definition_rejects_unknown_warband_relationship_type():
    with pytest.raises(
        TypeError,
        match=(
            "warband_member_relationship_type must be "
            "a FieldedModelRelationshipType or None"
        ),
    ):
        FieldedModelStructureDefinition(
            root_profile_id="WAR_MUMAK",
            members=(make_member(),),
            warband_member_relationship_type=(
                "HOWDAH_OCCUPANT_OF"
            ),
        )