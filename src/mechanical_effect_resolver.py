from collections import defaultdict

from fielded_model import FieldedModel
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from mechanical_effect_filter import (
    applicable_mechanical_effect_definitions,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)


def resolve_mechanical_effect_definitions(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
    fielded_model: FieldedModel,
) -> dict[
    MechanicalEffectTarget,
    tuple[
        MechanicalEffectDefinition,
        ...,
    ],
]:
    applicable = (
        applicable_mechanical_effect_definitions(
            definitions,
            fielded_model,
        )
    )

    grouped: dict[
        MechanicalEffectTarget,
        list[
            MechanicalEffectDefinition
        ],
    ] = defaultdict(list)

    for definition in applicable:
        grouped[
            definition.effect.target
        ].append(definition)

    return {
        target: tuple(target_definitions)
        for target, target_definitions
        in grouped.items()
    }