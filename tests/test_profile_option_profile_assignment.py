import pytest

from profile_option_profile_assignment import (
    ProfileOptionProfileAssignment,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)

def test_profile_option_profile_assignment_stores_profile_id():
    assignment = ProfileOptionProfileAssignment(
        profile_id="TROLL_BRUTE",
    )

    assert assignment.profile_id == "TROLL_BRUTE"


def test_profile_option_profile_assignment_rejects_empty_profile_id():
    with pytest.raises(
        ValueError,
        match="Assigned profile ID cannot be empty.",
    ):
        ProfileOptionProfileAssignment(
            profile_id="",
        )

def test_profile_assignment_can_store_relationship_type():
    assignment = ProfileOptionProfileAssignment(
        profile_id="TROLL_BRUTE",
        relationship_type=(
            FieldedModelRelationshipType
            .WAR_BEAST_COMMANDER_OF
        ),
    )

    assert (
        assignment.relationship_type
        is FieldedModelRelationshipType
        .WAR_BEAST_COMMANDER_OF
    )