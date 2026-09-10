from fielded_model import FieldedModel
from fielded_model_relationship import (
    FieldedModelRelationship,
)
from fielded_model_relationship_set import (
    FieldedModelRelationshipSet,
)


def build_fielded_model_relationship_set(
    fielded_models: tuple[FieldedModel, ...],
    relationships: tuple[
        FieldedModelRelationship,
        ...
    ] = (),
) -> FieldedModelRelationshipSet:
    return FieldedModelRelationshipSet(
        fielded_models=fielded_models,
        relationships=relationships,
    )