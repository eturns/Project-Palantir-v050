from fractions import Fraction
from functools import lru_cache
from defensive_state import DefensiveState
from fate_probability import (
    FATE_SUCCESS_TARGET,
    get_fate_prevention_probability_with_might,
)
from defensive_resolution import get_wounds_from_strike_damage
from strike_damage import StrikeDamage
from configured_profile import ConfiguredProfile
from special_rule_defensive_effect import (
    get_available_fate_attempts,
)

def get_survival_probability_after_one_wound(
    state: DefensiveState,
    might_points: int = 0,
    required_fate_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if might_points < 0:
        raise ValueError(
            "Might points cannot be negative."
        )

    if state.remaining_wounds == 0:
        return Fraction(0, 1)

    if state.remaining_wounds > 1:
        return Fraction(1, 1)

    return get_fate_prevention_probability_with_might(
        fate_points=state.remaining_fate,
        might_points=might_points,
        required_roll=required_fate_roll,
    )

def get_survival_probability_after_wounds(
    state: DefensiveState,
    incoming_wounds: int,
    might_points: int = 0,
    required_fate_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if incoming_wounds < 0:
        raise ValueError(
            "Incoming wounds cannot be negative."
        )

    if might_points < 0:
        raise ValueError(
            "Might points cannot be negative."
        )

    @lru_cache
    def survive(
        wounds_left: int,
        remaining_wounds: int,
        remaining_fate: int,
        remaining_might: int,
    ) -> Fraction:
        if remaining_wounds <= 0:
            return Fraction(0, 1)

        if wounds_left == 0:
            return Fraction(1, 1)

        return resolve_current_wound(
            wounds_left,
            remaining_wounds,
            remaining_fate,
            remaining_might,
        )

    @lru_cache
    def resolve_current_wound(
        wounds_left: int,
        remaining_wounds: int,
        remaining_fate: int,
        remaining_might: int,
    ) -> Fraction:
        # The player may choose not to spend Fate.
        accept_wound_probability = survive(
            wounds_left - 1,
            remaining_wounds - 1,
            remaining_fate,
            remaining_might,
        )

        if remaining_fate == 0:
            return accept_wound_probability

        fate_outcomes = []

        for natural_roll in range(1, 7):
            if natural_roll >= required_fate_roll:
                outcome = survive(
                    wounds_left - 1,
                    remaining_wounds,
                    remaining_fate - 1,
                    remaining_might,
                )

            else:
                # Leave this failed Fate roll unmodified.
                # The player may then spend another Fate point
                # or accept the Wound.
                outcome = resolve_current_wound(
                    wounds_left,
                    remaining_wounds,
                    remaining_fate - 1,
                    remaining_might,
                )

                might_required = (
                    required_fate_roll - natural_roll
                )

                if (
                    required_fate_roll <= 6
                    and might_required <= remaining_might
                ):
                    might_outcome = survive(
                        wounds_left - 1,
                        remaining_wounds,
                        remaining_fate - 1,
                        remaining_might - might_required,
                    )

                    outcome = max(
                        outcome,
                        might_outcome,
                    )

            fate_outcomes.append(outcome)

        spend_fate_probability = (
            sum(
                fate_outcomes,
                Fraction(0, 1),
            )
            / 6
        )

        return max(
            accept_wound_probability,
            spend_fate_probability,
        )

    return survive(
        incoming_wounds,
        state.remaining_wounds,
        state.remaining_fate,
        might_points,
    )

def get_survival_probability_after_strike_damage(
    state: DefensiveState,
    damage: StrikeDamage,
    might_points: int = 0,
    required_fate_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if might_points < 0:
        raise ValueError(
            "Might points cannot be negative."
        )

    if state.remaining_wounds == 0:
        return Fraction(0, 1)

    wounds_from_strike = get_wounds_from_strike_damage(
        damage,
    )

    if wounds_from_strike < state.remaining_wounds:
        return Fraction(1, 1)

    return get_fate_prevention_probability_with_might(
        fate_points=state.remaining_fate,
        might_points=might_points,
        required_roll=required_fate_roll,
    )

def get_configured_survival_probability_after_strike_damage(
    defender: ConfiguredProfile,
    state: DefensiveState,
    damage: StrikeDamage,
    might_points: int = 0,
    required_fate_roll: int = FATE_SUCCESS_TARGET,
) -> Fraction:
    if might_points < 0:
        raise ValueError(
            "Might points cannot be negative."
        )

    if state.remaining_wounds == 0:
        return Fraction(0, 1)

    wounds_from_strike = get_wounds_from_strike_damage(
        damage,
    )

    if wounds_from_strike < state.remaining_wounds:
        return Fraction(1, 1)

    available_fate_attempts = (
        get_available_fate_attempts(
            defender,
            state,
        )
    )

    return get_fate_prevention_probability_with_might(
        fate_points=available_fate_attempts,
        might_points=might_points,
        required_roll=required_fate_roll,
    )