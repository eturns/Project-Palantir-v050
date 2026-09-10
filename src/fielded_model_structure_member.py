from dataclasses import dataclass

from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)


@dataclass(frozen=True)
class FieldedModelStructureMember:
    profile_id: str
    relationship_type: FieldedModelRelationshipType

    def __post_init__(self) -> None:
        if not self.profile_id:
            raise ValueError(
                "Structure member profile id must not be empty."
            )

        if not isinstance(
            self.relationship_type,
            FieldedModelRelationshipType,
        ):
            raise TypeError(
                "relationship_type must be a "
                "FieldedModelRelationshipType."
            )