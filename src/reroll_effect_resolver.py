from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from reroll_mechanical_effect import (
    RerollMechanicalEffect,
)
from reroll_scope import RerollScope
from wound_reroll import WoundReroll


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


def resolved_wound_reroll(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> WoundReroll | None:
    if not definitions:
        return None

    scopes = resolved_reroll_scopes(
        definitions,
    )

    return WoundReroll(
        reroll_failed=(
            RerollScope.FAILED in scopes
        ),
        reroll_natural_ones=(
            RerollScope.NATURAL_ONES in scopes
        ),
    )