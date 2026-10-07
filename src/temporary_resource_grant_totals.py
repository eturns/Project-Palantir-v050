from temporary_resource_grant import (
    TemporaryResourceGrant,
)
from resource_owner import ResourceOwner
from resource_use_permission import ResourceType


def calculate_temporary_resource_total(
    grants: tuple[
        TemporaryResourceGrant,
        ...,
    ],
    owner: ResourceOwner,
    resource_type: ResourceType,
) -> int:
    return sum(
        grant.amount
        for grant in grants
        if (
            grant.owner == owner
            and grant.resource_type == resource_type
        )
    )