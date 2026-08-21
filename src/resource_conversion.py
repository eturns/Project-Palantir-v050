from dataclasses import dataclass

from resource_use import ResourceUse
from resource_use_permission import ResourceType


@dataclass(frozen=True)
class ResourceConversion:
    source_resource_type: ResourceType
    target_resource_use: ResourceUse