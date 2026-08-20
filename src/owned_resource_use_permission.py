from dataclasses import dataclass

from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


@dataclass(frozen=True)
class OwnedResourceUsePermission:
    owner: ResourceOwner
    resource_type: ResourceType
    resource_use: ResourceUse