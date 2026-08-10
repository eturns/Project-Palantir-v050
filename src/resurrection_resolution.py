from fractions import Fraction

from resurrection_probability import (
    UNHOLY_RESURRECTION_TARGET,
    get_resurrection_success_probability,
)
from resurrection_state import ResurrectionState


def get_state_after_model_is_slain(
    has_unholy_resurrection: bool,
) -> ResurrectionState:
    if has_unholy_resurrection:
        return ResurrectionState.MARKER

    return ResurrectionState.CASUALTY


def get_resurrection_outcome_probabilities(
    roll_modifier: int = 0,
    required_roll: int = UNHOLY_RESURRECTION_TARGET,
) -> dict[ResurrectionState, Fraction]:
    success_probability = (
        get_resurrection_success_probability(
            required_roll=required_roll,
            roll_modifier=roll_modifier,
        )
    )

    return {
        ResurrectionState.ALIVE: success_probability,
        ResurrectionState.CASUALTY: (
            Fraction(1, 1) - success_probability
        ),
    }