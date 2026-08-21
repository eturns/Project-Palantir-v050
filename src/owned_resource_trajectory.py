from owned_hero_resource_state import (
    OwnedHeroResourceState,
)
from owned_resource_allocation import (
    OwnedResourceAllocation,
)
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from owned_resource_turn_transition import (
    apply_owned_resource_turn,
)
from owned_resource_use_permission import (
    OwnedResourceUsePermission,
)


def calculate_owned_resource_trajectory(
    initial_states: tuple[
        OwnedHeroResourceState,
        ...,
    ],
    allocations_by_turn: tuple[
        tuple[
            OwnedResourceAllocation,
            ...,
        ],
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
) -> tuple[
    tuple[
        OwnedHeroResourceState,
        ...,
    ],
    ...,
]:
    trajectory = [initial_states]
    current_states = initial_states

    for allocations in allocations_by_turn:
        current_states = apply_owned_resource_turn(
            states=current_states,
            allocations=allocations,
            permissions=permissions,
            conversions=conversions,
        )
        trajectory.append(current_states)

    return tuple(trajectory)