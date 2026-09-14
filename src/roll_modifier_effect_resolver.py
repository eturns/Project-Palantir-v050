from duel_modifier import DuelModifier
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from roll_modifier_mechanical_effect import (
    RollModifierMechanicalEffect,
)
from wound_modifier import WoundModifier

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


def resolved_duel_modifier(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> DuelModifier | None:
    if not definitions:
        return None

    value = 0
    ignored_on_natural_six = False

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

        if effect.ignored_on_natural_six:
            ignored_on_natural_six = True

    return DuelModifier(
        value=value,
        ignored_on_natural_six=(
            ignored_on_natural_six
        ),
    )

def resolved_wound_modifier(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> WoundModifier:
    return WoundModifier(
        to_wound=combined_roll_modifier_value(
            definitions,
        ),
    )