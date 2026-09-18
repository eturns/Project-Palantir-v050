from dataclasses import dataclass
from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)

@dataclass(frozen=True)
class ProfileOptionProfileAssignment:
    profile_id: str
    relationship_type: (
        FieldedModelRelationshipType | None
    ) = None

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise ValueError(
                "Assigned profile ID cannot be empty."
            )