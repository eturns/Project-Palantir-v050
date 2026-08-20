from army import Army
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_owner import ResourceOwner


def get_initial_owned_resource_use_permissions(
    army: Army,
) -> tuple[OwnedResourceUsePermission, ...]:
    permissions: list[OwnedResourceUsePermission] = []

    for entry in sorted(
        army.entries,
        key=lambda army_entry: army_entry.profile.id,
    ):
        for instance_index in range(
            1,
            entry.quantity + 1,
        ):
            owner = ResourceOwner(
                profile_id=entry.profile.id,
                instance_index=instance_index,
            )

            for (
                resource_type,
                resource_use,
            ) in entry.profile.special_resource_permissions:
                permissions.append(
                    OwnedResourceUsePermission(
                        owner=owner,
                        resource_type=resource_type,
                        resource_use=resource_use,
                    )
                )

    return tuple(permissions)