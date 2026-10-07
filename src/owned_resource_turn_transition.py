from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_application import (
    apply_owned_resource_allocations,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from temporary_resource_grant import (
    TemporaryResourceGrant,
)


def apply_owned_resource_turn(
    states: tuple[
        OwnedHeroResourceState,
        ...,
    ],
    allocations: tuple[
        OwnedResourceAllocation,
        ...,
    ],
    permissions: tuple[
        OwnedResourceUsePermission,
        ...,
    ],
    conversions: tuple[
        OwnedResourceConversion,
        ...,
    ],
    temporary_grants: tuple[
        TemporaryResourceGrant,
        ...,
    ] = (),
) -> tuple[OwnedHeroResourceState, ...]:
    _ = temporary_grants

    return apply_owned_resource_allocations(
    states=states,
    allocations=allocations,
    permissions=permissions,
    conversions=conversions,
    temporary_grants=temporary_grants,
)