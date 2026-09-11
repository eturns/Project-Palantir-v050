from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from resource_permission_mechanical_effect import (
    ResourcePermissionMechanicalEffect,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def resolved_resource_permissions(
    definitions: tuple[
        MechanicalEffectDefinition,
        ...,
    ],
) -> set[
    tuple[
        ResourceType,
        ResourceUse,
    ]
]:
    permissions: set[
        tuple[
            ResourceType,
            ResourceUse,
        ]
    ] = set()

    for definition in definitions:
        effect = definition.effect

        if not isinstance(
            effect,
            ResourcePermissionMechanicalEffect,
        ):
            raise TypeError(
                "All definitions must contain "
                "ResourcePermissionMechanicalEffect "
                "values."
            )

        permissions.add(
            (
                effect.resource_type,
                effect.resource_use,
            )
        )

    return permissions