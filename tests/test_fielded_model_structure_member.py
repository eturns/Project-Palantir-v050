import pytest

from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_structure_member import (
    FieldedModelStructureMember,
)


def test_structure_member_preserves_values():
    member = FieldedModelStructureMember(
        profile_id="COMMANDER",
        relationship_type=(
            FieldedModelRelationshipType
            .WAR_BEAST_COMMANDER_OF
        ),
    )

    assert member.profile_id == "COMMANDER"
    assert member.relationship_type is (
        FieldedModelRelationshipType
        .WAR_BEAST_COMMANDER_OF
    )


def test_structure_member_rejects_empty_profile_id():
    with pytest.raises(
        ValueError,
        match="Structure member profile id",
    ):
        FieldedModelStructureMember(
            profile_id="",
            relationship_type=(
                FieldedModelRelationshipType
                .WAR_BEAST_COMMANDER_OF
            ),
        )


def test_structure_member_rejects_unknown_relationship_type():
    with pytest.raises(
        TypeError,
        match=(
            "relationship_type must be a "
            "FieldedModelRelationshipType"
        ),
    ):
        FieldedModelStructureMember(
            profile_id="COMMANDER",
            relationship_type="COMMANDER",
        )


def test_structure_member_can_represent_howdah_occupant():
    member = FieldedModelStructureMember(
        profile_id="HARADRIM_WARRIOR",
        relationship_type=(
            FieldedModelRelationshipType
            .HOWDAH_OCCUPANT_OF
        ),
    )

    assert member.relationship_type is (
        FieldedModelRelationshipType
        .HOWDAH_OCCUPANT_OF
    )