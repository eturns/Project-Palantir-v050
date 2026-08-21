from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


_UNHOLY_RESURRECTION = "UNHOLY_RESURRECTION"


def get_special_rule_resource_permissions(
    owner: ResourceOwner,
    special_rule_ids: tuple[str, ...],
) -> tuple[OwnedResourceUsePermission, ...]:
    permissions: list[OwnedResourceUsePermission] = []

    if _UNHOLY_RESURRECTION in special_rule_ids:
        permissions.append(
            OwnedResourceUsePermission(
                owner=owner,
                resource_type=ResourceType.WILL,
                resource_use=ResourceUse.BOOST_RESURRECTION,
            )
        )

    return tuple(permissions)