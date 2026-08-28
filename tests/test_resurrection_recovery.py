from fractions import Fraction

import pytest

from resurrection_recovery import (
    calculate_expected_resurrection_bonus,
)


def test_expected_resurrection_bonus_uses_model_fraction_and_probability():
    result = calculate_expected_resurrection_bonus(
        resurrection_capable_models=5,
        starting_models=10,
        success_probability=Fraction(2, 3),
    )

    assert result == pytest.approx(
        1 / 3,
    )


def test_expected_resurrection_bonus_is_zero_with_no_resurrection_models():
    result = calculate_expected_resurrection_bonus(
        resurrection_capable_models=0,
        starting_models=10,
        success_probability=Fraction(2, 3),
    )

    assert result == 0.0


def test_expected_resurrection_bonus_is_zero_when_resurrection_cannot_succeed():
    result = calculate_expected_resurrection_bonus(
        resurrection_capable_models=5,
        starting_models=10,
        success_probability=Fraction(0, 1),
    )

    assert result == 0.0


def test_expected_resurrection_bonus_is_one_when_entire_army_always_recovers():
    result = calculate_expected_resurrection_bonus(
        resurrection_capable_models=10,
        starting_models=10,
        success_probability=Fraction(1, 1),
    )

    assert result == 1.0


def test_resurrection_models_cannot_exceed_starting_models():
    with pytest.raises(ValueError):
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=11,
            starting_models=10,
            success_probability=Fraction(2, 3),
        )


def test_resurrection_models_cannot_be_negative():
    with pytest.raises(ValueError):
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=-1,
            starting_models=10,
            success_probability=Fraction(2, 3),
        )


def test_starting_models_must_be_positive():
    with pytest.raises(ValueError):
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=0,
            starting_models=0,
            success_probability=Fraction(2, 3),
        )


def test_success_probability_must_be_between_zero_and_one():
    with pytest.raises(ValueError):
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=5,
            starting_models=10,
            success_probability=1.1,
        )

def test_expected_resurrection_bonus_represents_one_resurrection_opportunity():
    result = calculate_expected_resurrection_bonus(
        resurrection_capable_models=5,
        starting_models=10,
        success_probability=Fraction(2, 3),
    )

    assert result == pytest.approx(
        (5 / 10) * (2 / 3)
    )

    assert result != pytest.approx(
        (5 / 10) * 2
    )