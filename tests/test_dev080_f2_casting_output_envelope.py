"""
Project Palantír
DEV-080-F2: Casting Output Envelope acceptance.

Author: Edward Turns (Project Lead)

Tests expected casting output with finite Will
and distinct-spell restrictions.
"""

import pytest

from magic_casting_output_envelope import (
    calculate_casting_output_envelope,
)


def test_single_caster_output():
    result = calculate_casting_output_envelope(
        spell_probabilities=(
            ("EASY", 0.75),
            ("HARD", 0.25),
        ),
        starting_will=6,
        hypothetical_activations=6,
        permitted_attempts_per_activation=1,
    )

    assert result.modelled_attempts == 6
    assert result.minimum_expected_successes == pytest.approx(
        1.5
    )
    assert result.maximum_expected_successes == pytest.approx(
        4.5
    )


def test_double_cast_uses_distinct_spells():
    result = calculate_casting_output_envelope(
        spell_probabilities=(
            ("EASY", 0.75),
            ("HARD", 0.25),
        ),
        starting_will=12,
        hypothetical_activations=6,
        permitted_attempts_per_activation=2,
    )

    assert result.modelled_attempts == 12
    assert result.minimum_expected_successes == pytest.approx(
        6.0
    )
    assert result.maximum_expected_successes == pytest.approx(
        6.0
    )


def test_zero_will_gives_zero_output():
    result = calculate_casting_output_envelope(
        spell_probabilities=(("EASY", 0.75),),
        starting_will=0,
    )

    assert result.modelled_attempts == 0
    assert result.minimum_expected_successes == 0
    assert result.maximum_expected_successes == 0


def test_reduced_will_should_spread_high_value_casts():
    """
    With three Will across three activations,
    the maximum is three EASY casts.

    Casting EASY and HARD together in one
    activation would be less effective.
    """
    result = calculate_casting_output_envelope(
        spell_probabilities=(
            ("EASY", 0.75),
            ("HARD", 0.25),
        ),
        starting_will=3,
        hypothetical_activations=3,
        permitted_attempts_per_activation=2,
    )

    assert result.modelled_attempts == 3
    assert result.maximum_expected_successes == pytest.approx(
        2.25
    )
