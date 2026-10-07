from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_legality import (
    validate_owned_resource_allocation,
)
from owned_resource_allocation_totals import (
    calculate_owned_resource_allocation_totals,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)
from resource_use_permission import ResourceType
from temporary_resource_grant import (
    TemporaryResourceGrant,
)
from temporary_resource_grant_totals import (
    calculate_temporary_resource_total,
)

def validate_owned_resource_allocations(
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
) -> None:
    states_by_owner = {
        state.owner: state
        for state in states
    }

    for allocation in allocations:
        if allocation.owner not in states_by_owner:
            raise ValueError(
                "No resource state exists for allocation owner."
            )

        validate_owned_resource_allocation(
            allocation=allocation,
            permissions=permissions,
            conversions=conversions,
        )

    totals = calculate_owned_resource_allocation_totals(
        allocations,
    )

    for (
        owner,
        resource_type,
    ), amount in totals.items():
        state = states_by_owner[owner].resources

        if resource_type == ResourceType.MIGHT:
            temporary_might = (
                calculate_temporary_resource_total(
                    grants=temporary_grants,
                    owner=owner,
                    resource_type=ResourceType.MIGHT,
                )
            )

            if (
                amount
                > state.remaining_might
                + temporary_might
            ):
                raise ValueError(
                    "Owned resource allocations exceed remaining Might."
                )

            continue

        if (
            resource_type == ResourceType.WILL
            and amount > state.remaining_will
        ):
            raise ValueError(
                "Owned resource allocations exceed remaining Will."
            )

        if (
            resource_type == ResourceType.FATE
            and amount > state.remaining_fate
        ):
            raise ValueError(
                "Owned resource allocations exceed remaining Fate."
            )