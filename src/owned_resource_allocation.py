from dataclasses import dataclass

from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType


@dataclass(frozen=True)
class OwnedResourceAllocation:
    owner: ResourceOwner
    resource_type: ResourceType
    resource_use: ResourceUse
    amount: int = 0

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError(
                "Allocated resource amount cannot be negative."
            )