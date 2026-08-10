from fractions import Fraction
import pytest
from fate_probability import (
    get_expected_fate_spent,
    get_fate_prevention_probability,
    get_fate_prevention_probability_with_might,
    get_fate_success_probability,
    get_fate_success_probability_with_might,
)


def test_standard_fate_roll_succeeds_on_four_plus():
    result = get_fate_success_probability()

    assert result == Fraction(1, 2)


def test_fate_probability_supports_alternative_target():
    result = get_fate_success_probability(
        required_roll=5,
    )

    assert result == Fraction(1, 3)


def test_fate_probability_can_be_automatic():
    result = get_fate_success_probability(
        required_roll=1,
    )

    assert result == Fraction(1, 1)


def test_fate_probability_can_be_impossible():
    result = get_fate_success_probability(
        required_roll=7,
    )

    assert result == Fraction(0, 1)

def test_zero_fate_points_cannot_prevent_wound():
    result = get_fate_prevention_probability(
        fate_points=0,
    )

    assert result == Fraction(0, 1)


def test_one_fate_point_has_standard_prevention_probability():
    result = get_fate_prevention_probability(
        fate_points=1,
    )

    assert result == Fraction(1, 2)


def test_two_fate_points_have_three_quarters_prevention_probability():
    result = get_fate_prevention_probability(
        fate_points=2,
    )

    assert result == Fraction(3, 4)


def test_three_fate_points_have_seven_eighths_prevention_probability():
    result = get_fate_prevention_probability(
        fate_points=3,
    )

    assert result == Fraction(7, 8)


def test_fate_prevention_probability_supports_alternative_target():
    result = get_fate_prevention_probability(
        fate_points=2,
        required_roll=5,
    )

    assert result == Fraction(5, 9)


def test_fate_prevention_probability_rejects_negative_fate():
    with pytest.raises(
        ValueError,
        match="Fate points cannot be negative.",
    ):
        get_fate_prevention_probability(
            fate_points=-1,
        )

def test_zero_fate_points_spends_no_fate():
    result = get_expected_fate_spent(
        fate_points=0,
    )

    assert result == Fraction(0, 1)


def test_one_available_fate_always_spends_one():
    result = get_expected_fate_spent(
        fate_points=1,
    )

    assert result == Fraction(1, 1)


def test_two_available_fate_spends_one_and_a_half_on_average():
    result = get_expected_fate_spent(
        fate_points=2,
    )

    assert result == Fraction(3, 2)


def test_three_available_fate_spends_seven_quarters_on_average():
    result = get_expected_fate_spent(
        fate_points=3,
    )

    assert result == Fraction(7, 4)


def test_expected_fate_spent_supports_alternative_target():
    result = get_expected_fate_spent(
        fate_points=2,
        required_roll=5,
    )

    assert result == Fraction(5, 3)


def test_expected_fate_spent_rejects_negative_fate():
    with pytest.raises(
        ValueError,
        match="Fate points cannot be negative.",
    ):
        get_expected_fate_spent(
            fate_points=-1,
        )

def test_standard_fate_with_no_might_remains_half():
    result = get_fate_success_probability_with_might(
        might_points=0,
    )

    assert result == Fraction(1, 2)


def test_one_might_improves_standard_fate_probability():
    result = get_fate_success_probability_with_might(
        might_points=1,
    )

    assert result == Fraction(2, 3)


def test_two_might_improves_standard_fate_probability():
    result = get_fate_success_probability_with_might(
        might_points=2,
    )

    assert result == Fraction(5, 6)


def test_three_might_can_guarantee_standard_fate():
    result = get_fate_success_probability_with_might(
        might_points=3,
    )

    assert result == Fraction(1, 1)


def test_fate_with_might_supports_alternative_target():
    result = get_fate_success_probability_with_might(
        might_points=1,
        required_roll=5,
    )

    assert result == Fraction(1, 2)


def test_fate_with_might_rejects_negative_might():
    with pytest.raises(
        ValueError,
        match="Might points cannot be negative.",
    ):
        get_fate_success_probability_with_might(
            might_points=-1,
        )

def test_two_fate_with_no_might_remains_three_quarters():
    result = get_fate_prevention_probability_with_might(
        fate_points=2,
        might_points=0,
    )

    assert result == Fraction(3, 4)


def test_two_fate_with_one_might_has_eight_ninths_prevention():
    result = get_fate_prevention_probability_with_might(
        fate_points=2,
        might_points=1,
    )

    assert result == Fraction(8, 9)


def test_two_fate_with_two_might_has_thirty_five_thirty_sixths_prevention():
    result = get_fate_prevention_probability_with_might(
        fate_points=2,
        might_points=2,
    )

    assert result == Fraction(35, 36)


def test_three_fate_with_one_might_has_twenty_six_twenty_sevenths_prevention():
    result = get_fate_prevention_probability_with_might(
        fate_points=3,
        might_points=1,
    )

    assert result == Fraction(26, 27)


def test_zero_fate_cannot_prevent_wound_even_with_might():
    result = get_fate_prevention_probability_with_might(
        fate_points=0,
        might_points=3,
    )

    assert result == Fraction(0, 1)


def test_fate_prevention_with_might_supports_alternative_target():
    result = get_fate_prevention_probability_with_might(
        fate_points=2,
        might_points=1,
        required_roll=5,
    )

    assert result == Fraction(3, 4)


def test_fate_prevention_with_might_rejects_negative_fate():
    with pytest.raises(
        ValueError,
        match="Fate points cannot be negative.",
    ):
        get_fate_prevention_probability_with_might(
            fate_points=-1,
            might_points=1,
        )


def test_fate_prevention_with_might_rejects_negative_might():
    with pytest.raises(
        ValueError,
        match="Might points cannot be negative.",
    ):
        get_fate_prevention_probability_with_might(
            fate_points=1,
            might_points=-1,
        )