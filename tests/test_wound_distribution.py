import pytest

from fractions import Fraction

from wound_probability import get_wound_distribution


def test_zero_strikes_always_causes_zero_wounds():
    assert get_wound_distribution(
        number_of_strikes=0,
        wound_probability=Fraction(1, 2),
    ) == (
        Fraction(1, 1),
    )


def test_one_strike_at_half_probability():
    assert get_wound_distribution(
        number_of_strikes=1,
        wound_probability=Fraction(1, 2),
    ) == (
        Fraction(1, 2),
        Fraction(1, 2),
    )


def test_two_strikes_at_half_probability():
    assert get_wound_distribution(
        number_of_strikes=2,
        wound_probability=Fraction(1, 2),
    ) == (
        Fraction(1, 4),
        Fraction(1, 2),
        Fraction(1, 4),
    )


def test_three_strikes_at_half_probability():
    assert get_wound_distribution(
        number_of_strikes=3,
        wound_probability=Fraction(1, 2),
    ) == (
        Fraction(1, 8),
        Fraction(3, 8),
        Fraction(3, 8),
        Fraction(1, 8),
    )


def test_zero_wound_probability_never_causes_wounds():
    assert get_wound_distribution(
        number_of_strikes=3,
        wound_probability=Fraction(0, 1),
    ) == (
        Fraction(1, 1),
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(0, 1),
    )


def test_certain_wound_probability_always_causes_maximum_wounds():
    assert get_wound_distribution(
        number_of_strikes=3,
        wound_probability=Fraction(1, 1),
    ) == (
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(0, 1),
        Fraction(1, 1),
    )


def test_wound_distribution_sums_to_one():
    distribution = get_wound_distribution(
        number_of_strikes=4,
        wound_probability=Fraction(1, 3),
    )

    assert sum(distribution) == Fraction(1, 1)


def test_negative_number_of_strikes_is_rejected():
    with pytest.raises(
        ValueError,
        match="number_of_strikes must not be negative",
    ):
        get_wound_distribution(
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
        get_wound_distribution(
            number_of_strikes=2,
            wound_probability=wound_probability,
        )