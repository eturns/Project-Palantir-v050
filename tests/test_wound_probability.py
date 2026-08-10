import pytest

from fractions import Fraction

from wound_probability import (
    get_wound_probability,
    get_modified_wound_probability_with_reroll,
    get_wound_probability_with_reroll,
)
from wound_target import WoundTarget
from wound_modifier import WoundModifier
from wound_reroll import WoundReroll

@pytest.mark.parametrize(
    (
        "target",
        "expected",
    ),
    [
        (
            WoundTarget(3),
            Fraction(2, 3),
        ),
        (
            WoundTarget(4),
            Fraction(1, 2),
        ),
        (
            WoundTarget(5),
            Fraction(1, 3),
        ),
        (
            WoundTarget(6),
            Fraction(1, 6),
        ),
        (
            WoundTarget(6, 4),
            Fraction(1, 12),
        ),
        (
            WoundTarget(6, 5),
            Fraction(1, 18),
        ),
        (
            WoundTarget(6, 6),
            Fraction(1, 36),
        ),
        (
            None,
            Fraction(0, 1),
        ),
    ],
)
def test_get_wound_probability(
    target: WoundTarget | None,
    expected: Fraction,
):
    assert get_wound_probability(target) == expected

def test_wound_reroll_uses_modified_target():
    result = get_modified_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=4,
        ),
        modifier=WoundModifier(
            to_wound=1,
        ),
        reroll=WoundReroll(
            reroll_failed=True,
        ),
    )

    assert result == Fraction(8, 9)


def test_wound_reroll_respects_impossible_modified_roll():
    result = get_modified_wound_probability_with_reroll(
        target=WoundTarget(
            first_roll=6,
        ),
        modifier=WoundModifier(
            to_wound=-1,
        ),
        reroll=WoundReroll(
            reroll_failed=True,
        ),
    )

    assert result == Fraction(0, 1)