from dataclasses import dataclass

from fielded_model import FieldedModel
from fielded_model_relationship import (
    FieldedModelRelationship,
)


@dataclass(frozen=True)
class FieldedModelRelationshipSet:
    fielded_models: tuple[FieldedModel, ...]
    relationships: tuple[FieldedModelRelationship, ...]

    def __post_init__(self) -> None:
        fielded_model_ids = {
            fielded_model.id
            for fielded_model in self.fielded_models
        }

        if len(fielded_model_ids) != len(self.fielded_models):
            raise ValueError(
                "FieldedModel ids must be unique."
            )

        for relationship in self.relationships:
            if (
                relationship.source_fielded_model_id
                not in fielded_model_ids
            ):
                raise ValueError(
                    "Relationship source must belong to "
                    "the fielded model set."
                )

            if (
                relationship.target_fielded_model_id
                not in fielded_model_ids
            ):
                raise ValueError(
                    "Relationship target must belong to "
                    "the fielded model set."
                )

        if len(set(self.relationships)) != len(
            self.relationships
        ):
            raise ValueError(
                "Duplicate fielded model relationships "
                "are not permitted."
            )