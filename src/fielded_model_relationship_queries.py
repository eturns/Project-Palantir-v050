from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)


def get_relationships_from_source(
    relationships: tuple[
        FieldedModelRelationship,
        ...
    ],
    source_fielded_model_id: str,
) -> tuple[FieldedModelRelationship, ...]:
    return tuple(
        relationship
        for relationship in relationships
        if (
            relationship.source_fielded_model_id
            == source_fielded_model_id
        )
    )


def get_relationships_to_target(
    relationships: tuple[
        FieldedModelRelationship,
        ...
    ],
    target_fielded_model_id: str,
) -> tuple[FieldedModelRelationship, ...]:
    return tuple(
        relationship
        for relationship in relationships
        if (
            relationship.target_fielded_model_id
            == target_fielded_model_id
        )
    )


def get_relationships_of_type(
    relationships: tuple[
        FieldedModelRelationship,
        ...
    ],
    relationship_type: FieldedModelRelationshipType,
) -> tuple[FieldedModelRelationship, ...]:
    return tuple(
        relationship
        for relationship in relationships
        if (
            relationship.relationship_type
            is relationship_type
        )
    )