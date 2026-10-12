"""DEV-077S-I2-E-B1 — RED tests for generic Courage roll modifiers.

These tests deliberately fail against pre-I2-E courage_test.py.
Copy to tests/test_dev077s_i2e_courage_modifiers.py before running.
They specify arithmetic of a supplied modifier, NOT Harbinger rule eligibility.
"""
from fractions import Fraction
import pytest

from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext, calculate_courage_test_success_probability
from profiles import Profile


def make_configured(courage="7+"):
    return ConfiguredProfile(profile=Profile(
        id="I2E_COURAGE_TEST", name="I2E Courage Test", points=10,
        movement=6, fight=3, shooting="4+", strength=3, defence=4,
        attacks=1, wounds=1, courage=courage, intelligence="7+",
        might=0, will=0, fate=0, max_in_army=0,
    ))


def test_minus_one_roll_modifier_reduces_seven_plus_success_to_fifteen_of_thirty_six():
    result = calculate_courage_test_success_probability(
        make_configured(), CourageTestContext(roll_modifier=-1),
    )
    assert result == Fraction(15, 36)


def test_plus_one_roll_modifier_improves_seven_plus_success_to_twenty_six_of_thirty_six():
    result = calculate_courage_test_success_probability(
        make_configured(), CourageTestContext(roll_modifier=1),
    )
    assert result == Fraction(26, 36)


def test_zero_modifier_preserves_existing_courage_probability():
    result = calculate_courage_test_success_probability(
        make_configured(), CourageTestContext(roll_modifier=0),
    )
    assert result == Fraction(21, 36)


def test_roll_modifiers_add_before_comparison_to_target():
    result = calculate_courage_test_success_probability(
        make_configured(), CourageTestContext(roll_modifier=-2),
    )
    assert result == Fraction(10, 36)


def test_automatic_pass_takes_precedence_over_negative_modifier():
    result = calculate_courage_test_success_probability(
        make_configured(), CourageTestContext(automatically_passes=True, roll_modifier=-3),
    )
    assert result == Fraction(1, 1)


@pytest.mark.parametrize("invalid", [True, 0.5, "-1", None])
def test_roll_modifier_must_be_integer_not_boolean(invalid):
    with pytest.raises((TypeError, ValueError)):
        CourageTestContext(roll_modifier=invalid)
