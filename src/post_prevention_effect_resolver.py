from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from post_prevention_effect import (
    PostPreventionEffect,
)
from post_prevention_mechanical_effect import (
    PostPreventionMechanicalEffect,
)


def resolved_post_prevention_effects(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> set[
    PostPreventionEffect
]:
    effects: set[
        PostPreventionEffect
    ] = set()

    for definition in definitions:
        effect = definition.effect

        if not isinstance(
            effect,
            PostPreventionMechanicalEffect,
        ):
            raise TypeError(
                "All definitions must contain "
                "PostPreventionMechanicalEffect "
                "values."
            )

        effects.add(
            effect.post_prevention_effect
        )

    return effects