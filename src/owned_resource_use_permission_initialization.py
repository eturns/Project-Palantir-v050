from army import Army
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_owner import ResourceOwner
from resource_permission_effect_resolver import (
    resolved_resource_permissions,
)
from resource_permission_mechanical_effect import (
    ResourcePermissionMechanicalEffect,
)
from special_rule_mechanical_effect_definitions import (
    get_special_rule_mechanical_effect_definitions,
)


def get_initial_owned_resource_use_permissions(
    army: Army,
) -> tuple[OwnedResourceUsePermission, ...]:
    permissions: list[OwnedResourceUsePermission] = []

    for fielded_model in army.fielded_models():
        if fielded_model.configured_profile is None:
            continue

        profile = (
            fielded_model
            .configured_profile
            .profile
        )

        owner = ResourceOwner(
            fielded_model_id=fielded_model.id,
        )

        for (
            resource_type,
            resource_use,
        ) in profile.special_resource_permissions:
            permissions.append(
                OwnedResourceUsePermission(
                    owner=owner,
                    resource_type=resource_type,
                    resource_use=resource_use,
                )
            )

        special_rule_definitions = (
            get_special_rule_mechanical_effect_definitions(
                fielded_model.configured_profile,
            )
        )

        permission_definitions = tuple(
            definition
            for definition in special_rule_definitions
            if isinstance(
                definition.effect,
                ResourcePermissionMechanicalEffect,
            )
        )

        generic_permissions = (
            resolved_resource_permissions(
                permission_definitions,
            )
        )

        for (
            resource_type,
            resource_use,
        ) in generic_permissions:
            permissions.append(
                OwnedResourceUsePermission(
                    owner=owner,
                    resource_type=resource_type,
                    resource_use=resource_use,
                )
            )

    return tuple(permissions)