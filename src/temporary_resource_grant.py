from dataclasses import dataclass

from resource_owner import ResourceOwner
from resource_use_permission import ResourceType


@dataclass(frozen=True)
class TemporaryResourceGrant:
    owner: ResourceOwner
    resource_type: ResourceType
    amount: int = 1

    def __post_init__(self) -> None:
        if not isinstance(
            self.owner,
            ResourceOwner,
        ):
            raise TypeError(
                "owner must be a ResourceOwner."
            )

        if not isinstance(
            self.resource_type,
            ResourceType,
        ):
            raise TypeError(
                "resource_type must be a ResourceType."
            )

        if self.amount < 0:
            raise ValueError(
                "Temporary resource amount cannot be negative."
            )