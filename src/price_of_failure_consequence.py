from defensive_resolution import (
    apply_unprevented_wounds,
)
from defensive_state import DefensiveState
from price_of_failure_state import (
    PriceOfFailureState,
)


def apply_price_of_failure_loss(
    state: DefensiveState,
    price_of_failure_state: PriceOfFailureState,
    *,
    lost_duel: bool,
) -> DefensiveState:
    if (
        not price_of_failure_state.can_use
        or not lost_duel
    ):
        return state

    return apply_unprevented_wounds(
        state,
        wounds=1,
    )