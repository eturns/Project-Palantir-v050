from hero_resource_spending import (
    spend_fate,
    spend_might,
    spend_will,
)
from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_allocation_totals import (
    calculate_owned_resource_allocation_totals,
)
from owned_resource_allocation_validation import (
    validate_owned_resource_allocations,
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

def apply_owned_resource_allocations(
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
    validate_owned_resource_allocations(
        states=states,
        allocations=allocations,
        permissions=permissions,
        conversions=conversions,
        temporary_grants=temporary_grants,
    )

    totals = calculate_owned_resource_allocation_totals(
        allocations,
    )

    updated_states: list[OwnedHeroResourceState] = []

    for state in states:
        resources = state.resources

        might_spend = totals.get(
            (
                state.owner,
                ResourceType.MIGHT,
            ),
            0,
        )

        will_spend = totals.get(
            (
                state.owner,
                ResourceType.WILL,
            ),
            0,
        )

        fate_spend = totals.get(
            (
                state.owner,
                ResourceType.FATE,
            ),
            0,
        )

        if might_spend:
            temporary_might = (
                calculate_temporary_resource_total(
                    grants=temporary_grants,
                    owner=state.owner,
                    resource_type=ResourceType.MIGHT,
                )
            )

            persistent_might_spend = max(
                might_spend - temporary_might,
                0,
            )

            if persistent_might_spend:
                resources = spend_might(
                    resources,
                    amount=persistent_might_spend,
                )

        if will_spend:
            resources = spend_will(
                resources,
                amount=will_spend,
            )

        if fate_spend:
            resources = spend_fate(
                resources,
                amount=fate_spend,
            )

        updated_states.append(
            OwnedHeroResourceState(
                owner=state.owner,
                resources=resources,
            )
        )

    return tuple(updated_states)