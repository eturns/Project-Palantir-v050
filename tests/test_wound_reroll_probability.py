from fractions import Fraction

from wound_probability import (
    get_wound_probability_with_reroll,
    get_modified_wound_probability_with_reroll,
)
from wound_reroll import WoundReroll
from wound_target import WoundTarget
from wound_modifier import WoundModifier


def test_failed_wound_reroll_improves_four_plus():
    result = get_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=4,
        ),
        reroll=WoundReroll(
            reroll_failed=True,
        ),
    )

    assert result == Fraction(3, 4)


def test_disabled_wound_reroll_preserves_probability():
    result = get_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=4,
        ),
        reroll=WoundReroll(),
    )

    assert result == Fraction(1, 2)


def test_failed_wound_reroll_applies_to_both_two_stage_rolls():
    result = get_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=6,
            second_roll=4,
        ),
        reroll=WoundReroll(
            reroll_failed=True,
        ),
    )

    assert result == Fraction(11, 48)

def test_modified_wound_reroll_applies_to_both_two_stage_rolls():
    result = get_modified_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=6,
            second_roll=4,
        ),
        modifier=WoundModifier(
            to_wound=1,
        ),
        reroll=WoundReroll(
            reroll_failed=True,
        ),
    )

    assert result == Fraction(40, 81)

def test_natural_one_reroll_improves_four_plus():
    result = get_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=4,
        ),
        reroll=WoundReroll(
            reroll_natural_ones=True,
        ),
    )

    assert result == Fraction(7, 12)


def test_natural_one_reroll_is_weaker_than_failed_reroll():
    natural_one_result = get_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=4,
        ),
        reroll=WoundReroll(
            reroll_natural_ones=True,
        ),
    )

    failed_result = get_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=4,
        ),
        reroll=WoundReroll(
            reroll_failed=True,
        ),
    )

    assert natural_one_result < failed_result

def test_natural_one_reroll_uses_natural_die_with_modifier():
    result = get_modified_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=3,
        ),
        modifier=WoundModifier(
            to_wound=2,
        ),
        reroll=WoundReroll(
            reroll_natural_ones=True,
        ),
    )

    assert result == Fraction(1, 1)