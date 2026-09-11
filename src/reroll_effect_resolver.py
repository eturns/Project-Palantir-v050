from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from reroll_mechanical_effect import (
    RerollMechanicalEffect,
)
from reroll_scope import RerollScope


def resolved_reroll_scopes(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> set[RerollScope]:
    scopes: set[RerollScope] = set()

    for definition in definitions:
        effect = definition.effect

        if not isinstance(
            effect,
            RerollMechanicalEffect,
        ):
            raise TypeError(
                "All definitions must contain "
                "RerollMechanicalEffect values."
            )

        scopes.add(effect.scope)

    return scopes