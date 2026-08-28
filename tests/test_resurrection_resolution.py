from fractions import Fraction

from resurrection_resolution import (
    get_resurrection_outcome_probabilities,
    get_state_after_model_is_slain,
)
from resurrection_state import ResurrectionState


def test_model_without_unholy_resurrection_becomes_casualty():
    result = get_state_after_model_is_slain(
        has_unholy_resurrection=False,
    )

    assert result == ResurrectionState.CASUALTY


def test_slain_model_with_unholy_resurrection_becomes_marker():
    result = get_state_after_model_is_slain(
        has_unholy_resurrection=True,
    )

    assert result == ResurrectionState.MARKER


def test_standard_resurrection_marker_returns_two_thirds_of_the_time():
    result = get_resurrection_outcome_probabilities()

    assert (
        result[ResurrectionState.ALIVE]
        == Fraction(2, 3)
    )


def test_standard_resurrection_marker_becomes_casualty_one_third_of_the_time():
    result = get_resurrection_outcome_probabilities()

    assert (
        result[ResurrectionState.CASUALTY]
        == Fraction(1, 3)
    )


def test_resurrection_modifier_changes_outcome_distribution():
    result = get_resurrection_outcome_probabilities(
        roll_modifier=-1,
    )

    assert (
        result[ResurrectionState.ALIVE]
        == Fraction(1, 2)
    )
    assert (
        result[ResurrectionState.CASUALTY]
        == Fraction(1, 2)
    )

def test_resurrected_model_can_trigger_unholy_resurrection_again():
    first_slain_state = get_state_after_model_is_slain(
        has_unholy_resurrection=True,
    )

    assert first_slain_state == ResurrectionState.MARKER

    resurrected_state = ResurrectionState.ALIVE

    assert resurrected_state == ResurrectionState.ALIVE

    second_slain_state = get_state_after_model_is_slain(
        has_unholy_resurrection=True,
    )

    assert second_slain_state == ResurrectionState.MARKER