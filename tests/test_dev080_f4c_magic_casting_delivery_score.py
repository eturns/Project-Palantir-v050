"""
Project Palantír
DEV-080-F4C: Magic Casting Delivery Acceptance.

Author: Edward Turns (Project Lead)

Validates provisional numerical casting delivery
without declaring an overall Magic capability score.
"""

import pytest

from magic_casting_delivery_score import (
    calculate_magic_casting_delivery,
)


def test_necromancer_casting_delivery():
    result = calculate_magic_casting_delivery(
        expected_successes_lower=20 / 3,
        expected_successes_upper=32 / 3,
        modelled_attempts=12,
    )

    assert result.lower_score == pytest.approx(5 / 9)
    assert result.upper_score == pytest.approx(8 / 9)
    assert result.reference_attempts == 12


def test_smaug_casting_delivery():
    result = calculate_magic_casting_delivery(
        expected_successes_lower=2,
        expected_successes_upper=4,
        modelled_attempts=6,
    )

    assert result.lower_score == pytest.approx(1 / 6)
    assert result.upper_score == pytest.approx(1 / 3)


def test_non_magic_army_scores_zero():
    result = calculate_magic_casting_delivery(
        expected_successes_lower=0,
        expected_successes_upper=0,
        modelled_attempts=0,
    )

    assert result.lower_score == 0
    assert result.upper_score == 0


def test_reference_ceiling_exceeded_is_not_clipped():
    result = calculate_magic_casting_delivery(
        expected_successes_lower=10,
        expected_successes_upper=13,
        modelled_attempts=14,
    )

    assert result.lower_score is None
    assert result.upper_score is None
    assert result.evidence_status == (
        "reference_ceiling_exceeded"
    )


def test_invalid_expected_successes_rejected():
    with pytest.raises(ValueError):
        calculate_magic_casting_delivery(
            expected_successes_lower=5,
            expected_successes_upper=4,
            modelled_attempts=6,
        )


def test_impossible_success_count_rejected():
    with pytest.raises(ValueError):
        calculate_magic_casting_delivery(
            expected_successes_lower=5,
            expected_successes_upper=7,
            modelled_attempts=6,
        )


def test_casting_delivery_is_not_overall_magic():
    result = calculate_magic_casting_delivery(
        expected_successes_lower=2,
        expected_successes_upper=4,
        modelled_attempts=6,
    )

    assert result.evidence_status == (
        "provisional_casting_delivery_only"
    )
    assert result.dashboard_score is None
    assert result.scenario_score is None
