from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import (
    ResourceType,
    is_resource_use_permitted,
)


def is_owned_resource_use_permitted(
    owner: ResourceOwner,
    resource_type: ResourceType,
    resource_use: ResourceUse,
    permissions: tuple[
        OwnedResourceUsePermission,
        ...,
    ],
) -> bool:
    if is_resource_use_permitted(
        resource_type=resource_type,
        resource_use=resource_use,
    ):
        return True

    return any(
        permission.owner == owner
        and permission.resource_type == resource_type
        and permission.resource_use == resource_use
        for permission in permissions
    )