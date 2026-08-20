from army_resource_state import ArmyResourceState
from owned_hero_resource_state import OwnedHeroResourceState


def aggregate_owned_hero_resource_states(
    owned_states: tuple[
        OwnedHeroResourceState,
        ...,
    ],
) -> ArmyResourceState:
    return ArmyResourceState(
        might=sum(
            state.resources.remaining_might
            for state in owned_states
        ),
        will=sum(
            state.resources.remaining_will
            for state in owned_states
        ),
        fate=sum(
            state.resources.remaining_fate
            for state in owned_states
        ),
    )