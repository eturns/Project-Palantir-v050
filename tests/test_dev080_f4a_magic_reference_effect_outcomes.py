"""
Project Palantír
DEV-080-F4A: Reference Spell Impact Acceptance.

Author: Edward Turns (Project Lead)

Tests quantified spell outcomes without
inventing tactical weights or targets.
"""

from fractions import Fraction

import pytest

from magic_reference_effect_outcomes import (
    calculate_reference_chill_soul,
    calculate_reference_transfix,
)


def test_chill_soul_expected_wound():
    result = calculate_reference_chill_soul(
        effect_probability=Fraction(5, 9),
        target_eligible=True,
        wound_prevention_excluded=True,
    )

    assert result.expected_wounds == Fraction(5, 9)
    assert result.expected_denied_activations is None
    assert result.evidence_status == (
        "conditional_wound_outcome"
    )


def test_chill_soul_unresolved_prevention():
    result = calculate_reference_chill_soul(
        effect_probability=Fraction(5, 9),
        target_eligible=True,
        wound_prevention_excluded=False,
    )

    assert result.expected_wounds is None
    assert result.evidence_status == (
        "reference_context_incomplete"
    )


def test_transfix_expected_activation_denial():
    result = calculate_reference_transfix(
        effect_probability=Fraction(8, 9),
        target_eligible=True,
        activation_remaining=True,
    )

    assert result.expected_denied_activations == Fraction(8, 9)
    assert result.expected_wounds is None


def test_transfix_already_activated():
    result = calculate_reference_transfix(
        effect_probability=Fraction(8, 9),
        target_eligible=True,
        activation_remaining=False,
    )

    assert result.expected_denied_activations == 0


def test_unverified_target_not_scored():
    result = calculate_reference_transfix(
        effect_probability=Fraction(8, 9),
        target_eligible=False,
        activation_remaining=True,
    )

    assert result.expected_denied_activations is None


@pytest.mark.parametrize(
    "probability",
    [
        Fraction(-1, 9),
        Fraction(10, 9),
    ],
)
def test_invalid_probabilities_rejected(probability):
    with pytest.raises(ValueError):
        calculate_reference_chill_soul(
            effect_probability=probability,
            target_eligible=True,
            wound_prevention_excluded=True,
        )


def test_reference_outputs_remain_uncalibrated():
    result = calculate_reference_chill_soul(
        effect_probability=Fraction(1, 2),
        target_eligible=True,
        wound_prevention_excluded=True,
    )

    assert result.dashboard_score is None
    assert result.scenario_score is None
