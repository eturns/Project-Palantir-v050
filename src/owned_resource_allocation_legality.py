from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_conversion_legality import (
    is_owned_resource_conversion_permitted,
)
from owned_resource_use_legality import (
    is_owned_resource_use_permitted,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_conversion import ResourceConversion


def validate_owned_resource_allocation(
    allocation: OwnedResourceAllocation,
    permissions: tuple[
        OwnedResourceUsePermission,
        ...,
    ],
    conversions: tuple[
        OwnedResourceConversion,
        ...,
    ],
) -> None:
    if is_owned_resource_use_permitted(
        owner=allocation.owner,
        resource_type=allocation.resource_type,
        resource_use=allocation.resource_use,
        permissions=permissions,
    ):
        return

    conversion = ResourceConversion(
        source_resource_type=allocation.resource_type,
        target_resource_use=allocation.resource_use,
    )

    if is_owned_resource_conversion_permitted(
        owner=allocation.owner,
        conversion=conversion,
        conversions=conversions,
    ):
        return

    raise ValueError(
        "Owned resource allocation is not permitted."
    )