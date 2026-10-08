from fractions import Fraction

import pytest

from in_the_way_probability import (
    get_in_the_way_success_probability,
)


@pytest.mark.parametrize(
    ("required_roll", "expected"),
    (
        (2, Fraction(5, 6)),
        (3, Fraction(4, 6)),
        (4, Fraction(3, 6)),
        (5, Fraction(2, 6)),
        (6, Fraction(1, 6)),
    ),
)
def test_in_the_way_probability_uses_required_roll(
    required_roll,
    expected,
):
    assert (
        get_in_the_way_success_probability(
            required_roll=required_roll,
        )
        == expected
    )


@pytest.mark.parametrize(
    "required_roll",
    (
        1,
        7,
        0,
        -1,
    ),
)
def test_in_the_way_probability_rejects_invalid_target(
    required_roll,
):
    with pytest.raises(ValueError):
        get_in_the_way_success_probability(
            required_roll=required_roll,
        )

@pytest.mark.parametrize(
    ("required_roll", "modifier", "expected"),
    (
        (4, 0, Fraction(3, 6)),
        (4, 1, Fraction(4, 6)),
        (4, -1, Fraction(2, 6)),
        (3, 1, Fraction(5, 6)),
        (5, -1, Fraction(1, 6)),
    ),
)
def test_in_the_way_probability_applies_modifier(
    required_roll,
    modifier,
    expected,
):
    assert (
        get_in_the_way_success_probability(
            required_roll=required_roll,
            modifier=modifier,
        )
        == expected
    )

@pytest.mark.parametrize(
    ("required_roll", "modifier", "expected"),
    (
        (2, 1, Fraction(1, 1)),
        (2, 5, Fraction(1, 1)),
        (6, -1, Fraction(0, 1)),
        (6, -5, Fraction(0, 1)),
    ),
)
def test_in_the_way_probability_clamps_extreme_modifiers(
    required_roll,
    modifier,
    expected,
):
    assert (
        get_in_the_way_success_probability(
            required_roll=required_roll,
            modifier=modifier,
        )
        == expected
    )