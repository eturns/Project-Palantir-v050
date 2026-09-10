from army import Army
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_owner import ResourceOwner
from special_rule_resource_permissions import (
    get_special_rule_resource_permissions,
)


def get_initial_owned_resource_use_permissions(
    army: Army,
) -> tuple[OwnedResourceUsePermission, ...]:
    permissions: list[OwnedResourceUsePermission] = []

    for fielded_model in army.fielded_models():
        profile = (
            fielded_model
            .configured_profile
            .profile
        )

        owner = ResourceOwner(
            fielded_model_id=fielded_model.id,
        )

        special_rule_ids = tuple(
            assignment.rule.id
            for assignment in profile.special_rules
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

        permissions.extend(
            get_special_rule_resource_permissions(
                owner=owner,
                special_rule_ids=special_rule_ids,
            )
        )

    return tuple(permissions)