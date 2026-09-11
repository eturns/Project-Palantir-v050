from fielded_model import FieldedModel
from mechanical_effect_applicability_matcher import (
    mechanical_effect_applies_to_fielded_model,
)
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)


def mechanical_effect_definition_applies_to_fielded_model(
    definition: MechanicalEffectDefinition,
    fielded_model: FieldedModel,
) -> bool:
    return mechanical_effect_applies_to_fielded_model(
        definition.applicability,
        fielded_model,
    )