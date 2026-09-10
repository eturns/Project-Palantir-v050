from dataclasses import dataclass

from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)


@dataclass(frozen=True)
class FieldedModelRelationship:
    source_fielded_model_id: str
    target_fielded_model_id: str
    relationship_type: FieldedModelRelationshipType

    def __post_init__(self) -> None:
        if not self.source_fielded_model_id:
            raise ValueError(
                "Source fielded model id must not be empty."
            )

        if not self.target_fielded_model_id:
            raise ValueError(
                "Target fielded model id must not be empty."
            )

        if (
            self.source_fielded_model_id
            == self.target_fielded_model_id
        ):
            raise ValueError(
                "A FieldedModel cannot relate to itself."
            )

        if not isinstance(
            self.relationship_type,
            FieldedModelRelationshipType,
        ):
            raise TypeError(
                "relationship_type must be a "
                "FieldedModelRelationshipType."
            )