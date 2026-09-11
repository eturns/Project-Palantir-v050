from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from roll_modifier_mechanical_effect import (
    RollModifierMechanicalEffect,
)


def combined_roll_modifier_value(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> int:
    value = 0

    for definition in definitions:
        effect = definition.effect

        if not isinstance(
            effect,
            RollModifierMechanicalEffect,
        ):
            raise TypeError(
                "All definitions must contain "
                "RollModifierMechanicalEffect values."
            )

        value += effect.value

    return value