from fielded_model import FieldedModel
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from mechanical_effect_definition_matcher import (
    mechanical_effect_definition_applies_to_fielded_model,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)


def applicable_mechanical_effect_definitions(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
    fielded_model: FieldedModel,
    target: MechanicalEffectTarget | None = None,
) -> tuple[
    MechanicalEffectDefinition,
    ...,
]:
    applicable = tuple(
        definition
        for definition in definitions
        if (
            mechanical_effect_definition_applies_to_fielded_model(
                definition,
                fielded_model,
            )
            and (
                target is None
                or definition.effect.target is target
            )
        )
    )

    return applicable