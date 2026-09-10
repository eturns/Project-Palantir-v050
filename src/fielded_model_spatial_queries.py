from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_set import (
    FieldedModelRelationshipSet,
)
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)


SPATIALLY_LINKED_RELATIONSHIP_TYPES = (
    FieldedModelRelationshipType.PASSENGER_OF,
    FieldedModelRelationshipType.WAR_BEAST_COMMANDER_OF,
    FieldedModelRelationshipType.HOWDAH_OCCUPANT_OF,
)


def spatial_relationships(
    relationship_set: FieldedModelRelationshipSet,
) -> tuple[FieldedModelRelationship, ...]:
    return tuple(
        relationship
        for relationship in relationship_set.relationships
        if (
            relationship.relationship_type
            in SPATIALLY_LINKED_RELATIONSHIP_TYPES
        )
    )