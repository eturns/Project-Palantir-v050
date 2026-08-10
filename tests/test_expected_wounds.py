import pytest

from fractions import Fraction

from wound_probability import get_expected_wounds


def test_zero_strikes_has_zero_expected_wounds():
    assert get_expected_wounds(
        number_of_strikes=0,
        wound_probability=Fraction(1, 2),
    ) == Fraction(0, 1)


def test_one_strike_expected_wounds_matches_probability():
    assert get_expected_wounds(
        number_of_strikes=1,
        wound_probability=Fraction(1, 3),
    ) == Fraction(1, 3)


def test_two_strikes_at_half_probability():
    assert get_expected_wounds(
        number_of_strikes=2,
        wound_probability=Fraction(1, 2),
    ) == Fraction(1, 1)


def test_three_strikes_at_one_third_probability():
    assert get_expected_wounds(
        number_of_strikes=3,
        wound_probability=Fraction(1, 3),
    ) == Fraction(1, 1)


def test_four_strikes_at_one_sixth_probability():
    assert get_expected_wounds(
        number_of_strikes=4,
        wound_probability=Fraction(1, 6),
    ) == Fraction(2, 3)


def test_zero_wound_probability_has_zero_expected_wounds():
    assert get_expected_wounds(
        number_of_strikes=4,
        wound_probability=Fraction(0, 1),
    ) == Fraction(0, 1)


def test_certain_wounds_equals_number_of_strikes():
    assert get_expected_wounds(
        number_of_strikes=4,
        wound_probability=Fraction(1, 1),
    ) == Fraction(4, 1)


def test_negative_number_of_strikes_is_rejected():
    with pytest.raises(
        ValueError,
        match="number_of_strikes must not be negative",
    ):
        get_expected_wounds(
            number_of_strikes=-1,
            wound_probability=Fraction(1, 2),
        )


@pytest.mark.parametrize(
    "wound_probability",
    [
        Fraction(-1, 6),
        Fraction(7, 6),
    ],
)
def test_invalid_wound_probability_is_rejected(
    wound_probability: Fraction,
):
    with pytest.raises(
        ValueError,
        match="wound_probability must be between 0 and 1",
    ):
        get_expected_wounds(
            number_of_strikes=2,
            wound_probability=wound_probability,
        )