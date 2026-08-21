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

    for entry in sorted(
        army.entries,
        key=lambda army_entry: army_entry.profile.id,
    ):
        profile = entry.profile

        special_rule_ids = tuple(
            assignment.rule.id
            for assignment in profile.special_rules
        )

        for instance_index in range(
            1,
            entry.quantity + 1,
        ):
            owner = ResourceOwner(
                profile_id=profile.id,
                instance_index=instance_index,
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