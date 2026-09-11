from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from strike_damage_mechanical_effect import (
    StrikeDamageMechanicalEffect,
)
from strike_damage import StrikeDamage


def resolved_strike_damage_effects(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> tuple[
    StrikeDamage,
    ...,
]:
    resolved: list[StrikeDamage] = []

    for definition in definitions:
        effect = definition.effect

        if not isinstance(
            effect,
            StrikeDamageMechanicalEffect,
        ):
            raise TypeError(
                "All definitions must contain "
                "StrikeDamageMechanicalEffect values."
            )

        resolved.append(
            effect.strike_damage
        )

    return tuple(resolved)