from hero_resource_spending import (
    spend_fate,
    spend_might,
    spend_will,
)
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_conversion import OwnedResourceConversion
from resource_use_permission import ResourceType


def apply_owned_resource_conversion_spend(
    state: OwnedHeroResourceState,
    conversion: OwnedResourceConversion,
    amount: int = 1,
) -> OwnedHeroResourceState:
    if state.owner != conversion.owner:
        raise ValueError(
            "Resource conversion owner does not match resource state owner."
        )

    source_resource_type = (
        conversion.conversion.source_resource_type
    )

    if source_resource_type == ResourceType.MIGHT:
        updated_resources = spend_might(
            state.resources,
            amount=amount,
        )
    elif source_resource_type == ResourceType.WILL:
        updated_resources = spend_will(
            state.resources,
            amount=amount,
        )
    elif source_resource_type == ResourceType.FATE:
        updated_resources = spend_fate(
            state.resources,
            amount=amount,
        )
    else:
        raise ValueError(
            "Unsupported resource conversion source type."
        )

    return OwnedHeroResourceState(
        owner=state.owner,
        resources=updated_resources,
    )