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
from combat_side import CombatSide
from profiles import Profile


def resolve_mechanical_effect_definitions(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
    fielded_model: FieldedModel,
    related_models: tuple[FieldedModel, ...] = (),
    combat_side: CombatSide | None = None,
) -> dict[
    MechanicalEffectTarget,
    tuple[
        MechanicalEffectDefinition,
        ...,
    ],
]:

    related_profiles: tuple[Profile, ...] = ()

    if combat_side is not None:
        subject_profile = (
            fielded_model
            .configured_profile
            .profile
        )

        related_profiles = tuple(
            participant.profile
            for participant in combat_side.participants
            if participant.profile is not subject_profile
        )

    applicable = (
        applicable_mechanical_effect_definitions(
            definitions,
            fielded_model,
            related_models=related_models,
            related_profiles=related_profiles,
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