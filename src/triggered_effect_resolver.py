from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from post_combat_wound_effect import (
    PostCombatWoundEffect,
)
from triggered_mechanical_effect import (
    TriggeredMechanicalEffect,
)


def resolved_triggered_effects(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> tuple[
    PostCombatWoundEffect,
    ...,
]:
    resolved: list[
        PostCombatWoundEffect
    ] = []

    for definition in definitions:
        effect = definition.effect

        if not isinstance(
            effect,
            TriggeredMechanicalEffect,
        ):
            raise TypeError(
                "All definitions must contain "
                "TriggeredMechanicalEffect values."
            )

        resolved.append(
            effect.triggered_effect
        )

    return tuple(resolved)