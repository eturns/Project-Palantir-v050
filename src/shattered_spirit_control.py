from shattered_spirit_state import (
    ShatteredSpiritState,
)


def is_opponent_controlled(
    state: ShatteredSpiritState | None,
) -> bool:
    if state is None:
        return False

    return state.is_opponent_controlled


def can_owner_choose_activation(
    state: ShatteredSpiritState | None,
) -> bool:
    return not is_opponent_controlled(state)