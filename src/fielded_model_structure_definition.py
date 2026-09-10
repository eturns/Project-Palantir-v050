from dataclasses import dataclass

from fielded_model_relationship_type import (
    FieldedModelRelationshipType,
)
from fielded_model_structure_member import (
    FieldedModelStructureMember,
)


@dataclass(frozen=True)
class FieldedModelStructureDefinition:
    root_profile_id: str
    members: tuple[
        FieldedModelStructureMember,
        ...
    ]
    warband_member_relationship_type: (
        FieldedModelRelationshipType | None
    ) = None

    def __post_init__(self) -> None:
        if not self.root_profile_id:
            raise ValueError(
                "Structure root profile id must not be empty."
            )

        if not self.members:
            raise ValueError(
                "Structure definition must contain "
                "at least one member."
            )

        if (
            self.warband_member_relationship_type
            is not None
            and not isinstance(
                self.warband_member_relationship_type,
                FieldedModelRelationshipType,
            )
        ):
            raise TypeError(
                "warband_member_relationship_type must be "
                "a FieldedModelRelationshipType or None."
            )