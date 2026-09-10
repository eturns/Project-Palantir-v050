import pytest

from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)


def test_fielded_model_relationship_preserves_values():
    relationship = FieldedModelRelationship(
        source_fielded_model_id="GIMLI:1:1",
        target_fielded_model_id="LEGOLAS:1:1",
        relationship_type=(
            FieldedModelRelationshipType.PASSENGER_OF
        ),
    )

    assert relationship.source_fielded_model_id == (
        "GIMLI:1:1"
    )

    assert relationship.target_fielded_model_id == (
        "LEGOLAS:1:1"
    )

    assert relationship.relationship_type is (
        FieldedModelRelationshipType.PASSENGER_OF
    )


def test_fielded_model_relationship_rejects_empty_source():
    with pytest.raises(
        ValueError,
        match="Source fielded model id must not be empty.",
    ):
        FieldedModelRelationship(
            source_fielded_model_id="",
            target_fielded_model_id="LEGOLAS:1:1",
            relationship_type=(
                FieldedModelRelationshipType.PASSENGER_OF
            ),
        )


def test_fielded_model_relationship_rejects_empty_target():
    with pytest.raises(
        ValueError,
        match="Target fielded model id must not be empty.",
    ):
        FieldedModelRelationship(
            source_fielded_model_id="GIMLI:1:1",
            target_fielded_model_id="",
            relationship_type=(
                FieldedModelRelationshipType.PASSENGER_OF
            ),
        )


def test_fielded_model_relationship_rejects_self_relationship():
    with pytest.raises(
        ValueError,
        match="A FieldedModel cannot relate to itself.",
    ):
        FieldedModelRelationship(
            source_fielded_model_id="GIMLI:1:1",
            target_fielded_model_id="GIMLI:1:1",
            relationship_type=(
                FieldedModelRelationshipType.PASSENGER_OF
            ),
        )


def test_fielded_model_relationship_rejects_unknown_type():
    with pytest.raises(
        TypeError,
        match=(
            "relationship_type must be a "
            "FieldedModelRelationshipType."
        ),
    ):
        FieldedModelRelationship(
            source_fielded_model_id="GIMLI:1:1",
            target_fielded_model_id="LEGOLAS:1:1",
            relationship_type="PASSENGER_OF",
        )