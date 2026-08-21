from dataclasses import dataclass

from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner


@dataclass(frozen=True)
class OwnedResourceConversion:
    owner: ResourceOwner
    conversion: ResourceConversion