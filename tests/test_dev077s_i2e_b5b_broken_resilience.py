"""DEV-077S-I2-E-B5-B1 RED: one-window Broken-army resilience.

Contract under test (not yet implemented):
* A surviving fielded model gets one Broken-army Courage opportunity.
* A provider's Stand Fast activates only if its own test passes.
* Explicit recipient coverage is supplied by the caller. No invented positions.
* Fractions are retained exactly; no arbitrary bonuses or independence
  assumption between recipients sharing the same provider.
* Results are expected *counts*, not probabilities of winning the game.
"""
from fractions import Fraction

import pytest

from army_broken_courage_resilience import (
    BrokenCourageParticipant,
    StandFastCoverage,
    calculate_broken_courage_resilience,
)


def participant(model_id: str, pass_chance: Fraction, *, warrior: bool = True):
    return BrokenCourageParticipant(
        model_id=model_id,
        individual_pass_probability=pass_chance,
        is_warrior=warrior,
    )


def test_empty_survivor_set_returns_zero_expected_retention():
    result = calculate_broken_courage_resilience((), army_is_broken=True)
    assert result.surviving_model_count == 0
    assert result.expected_retained_models == Fraction(0)
    assert result.expected_fleeing_models == Fraction(0)


def test_unbroken_army_retains_all_without_broken_courage_tests():
    models = (participant('A', Fraction(21, 36)), participant('B', Fraction(1, 2)))
    result = calculate_broken_courage_resilience(models, army_is_broken=False)
    assert result.expected_retained_models == Fraction(2)
    assert result.expected_fleeing_models == Fraction(0)


def test_broken_army_without_support_sums_exact_individual_pass_chances():
    models = (participant('A', Fraction(21, 36)), participant('B', Fraction(33, 36)))
    result = calculate_broken_courage_resilience(models, army_is_broken=True)
    assert result.expected_retained_models == Fraction(54, 36)
    assert result.expected_fleeing_models == Fraction(18, 36)
    assert result.retention_fraction == Fraction(54, 72)


def test_guaranteed_provider_pass_saves_eligible_recipient():
    models = (participant('H', Fraction(1), warrior=False),
              participant('W', Fraction(21, 36)))
    result = calculate_broken_courage_resilience(
        models, army_is_broken=True,
        stand_fast_coverage=(StandFastCoverage(provider_id='H', recipient_id='W'),),
    )
    assert result.expected_retained_models == Fraction(2)


def test_provider_test_is_not_assumed_to_pass():
    models = (participant('H', Fraction(1, 2), warrior=False),
              participant('W', Fraction(1, 2)))
    result = calculate_broken_courage_resilience(
        models, army_is_broken=True,
        stand_fast_coverage=(StandFastCoverage(provider_id='H', recipient_id='W'),),
    )
    # P(W retained) = P(H passes) + P(H fails)*P(W passes) = 3/4.
    # H itself survives the window with probability 1/2.
    assert result.expected_retained_models == Fraction(5, 4)
    assert result.expected_fleeing_models == Fraction(3, 4)


def test_absent_coverage_never_assumes_hero_support():
    models = (participant('H', Fraction(1), warrior=False),
              participant('W', Fraction(1, 2)))
    result = calculate_broken_courage_resilience(models, army_is_broken=True)
    assert result.expected_retained_models == Fraction(3, 2)


def test_two_recipients_sharing_provider_are_not_two_independent_provider_rolls():
    models = (participant('H', Fraction(1, 2), warrior=False),
              participant('W1', Fraction(1, 2)),
              participant('W2', Fraction(1, 2)))
    result = calculate_broken_courage_resilience(
        models, army_is_broken=True,
        stand_fast_coverage=(
            StandFastCoverage(provider_id='H', recipient_id='W1'),
            StandFastCoverage(provider_id='H', recipient_id='W2'),
        ),
    )
    assert result.expected_retained_models == Fraction(2)


def test_invalid_or_duplicate_model_identity_is_rejected():
    models = (participant('A', Fraction(1, 2)), participant('A', Fraction(1, 2)))
    with pytest.raises(ValueError, match='duplicate|unique'):
        calculate_broken_courage_resilience(models, army_is_broken=True)


def test_invalid_probability_is_rejected():
    with pytest.raises(ValueError, match='probability|range'):
        calculate_broken_courage_resilience(
            (participant('A', Fraction(3, 2)),), army_is_broken=True,
        )


def test_unknown_provider_is_rejected_not_assumed_available():
    with pytest.raises(ValueError, match='provider|unknown'):
        calculate_broken_courage_resilience(
            (participant('W', Fraction(1, 2)),), army_is_broken=True,
            stand_fast_coverage=(StandFastCoverage(provider_id='MISSING', recipient_id='W'),),
        )
