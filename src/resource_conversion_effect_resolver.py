from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from resource_conversion import ResourceConversion
from resource_conversion_mechanical_effect import (
    ResourceConversionMechanicalEffect,
)


def resolved_resource_conversions(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> set[
    ResourceConversion
]:
    conversions: set[
        ResourceConversion
    ] = set()

    for definition in definitions:
        effect = definition.effect

        if not isinstance(
            effect,
            ResourceConversionMechanicalEffect,
        ):
            raise TypeError(
                "All definitions must contain "
                "ResourceConversionMechanicalEffect "
                "values."
            )

        conversions.add(
            ResourceConversion(
                source_resource_type=(
                    effect.source_resource_type
                ),
                target_resource_use=(
                    effect.target_resource_use
                ),
            )
        )

    return conversions