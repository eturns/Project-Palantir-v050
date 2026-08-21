from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from resource_owner import ResourceOwner
from resource_use_permission import ResourceType


def calculate_owned_resource_allocation_totals(
    allocations: tuple[
        OwnedResourceAllocation,
        ...,
    ],
) -> dict[
    tuple[ResourceOwner, ResourceType],
    int,
]:
    totals: dict[
        tuple[ResourceOwner, ResourceType],
        int,
    ] = {}

    for allocation in allocations:
        key = (
            allocation.owner,
            allocation.resource_type,
        )

        totals[key] = (
            totals.get(key, 0)
            + allocation.amount
        )

    return totals