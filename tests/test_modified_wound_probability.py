from fractions import Fraction

import pytest

from wound_modifier import WoundModifier
from wound_probability import get_modified_wound_probability
from wound_target import WoundTarget


def test_no_modifier_preserves_probability():
    assert get_modified_wound_probability(
        WoundTarget(4),
        WoundModifier(),
    ) == Fraction(1, 2)


def test_positive_modifier_improves_wound_roll():
    assert get_modified_wound_probability(
        WoundTarget(4),
        WoundModifier(to_wound=1),
    ) == Fraction(2, 3)


def test_positive_modifier_can_produce_effective_two_plus():
    assert get_modified_wound_probability(
        WoundTarget(3),
        WoundModifier(to_wound=1),
    ) == Fraction(5, 6)


def test_modifier_can_make_wound_roll_automatic():
    assert get_modified_wound_probability(
        WoundTarget(3),
        WoundModifier(to_wound=2),
    ) == Fraction(1, 1)


def test_negative_modifier_makes_wounding_harder():
    assert get_modified_wound_probability(
        WoundTarget(5),
        WoundModifier(to_wound=-1),
    ) == Fraction(1, 6)


def test_impossible_target_remains_impossible():
    assert get_modified_wound_probability(
        None,
        WoundModifier(to_wound=1),
    ) == Fraction(0, 1)


def test_negative_modifier_can_make_wound_roll_impossible():
    assert get_modified_wound_probability(
        WoundTarget(6),
        WoundModifier(to_wound=-1),
    ) == Fraction(0, 1)


def test_positive_modifier_applies_to_both_two_stage_rolls():
    assert get_modified_wound_probability(
        WoundTarget(6, 4),
        WoundModifier(to_wound=1),
    ) == Fraction(2, 9)

def test_positive_modifier_applies_to_six_five_two_stage_roll():
    assert get_modified_wound_probability(
        WoundTarget(6, 5),
        WoundModifier(to_wound=1),
    ) == Fraction(1, 6)


def test_positive_modifier_applies_to_six_six_two_stage_roll():
    assert get_modified_wound_probability(
        WoundTarget(6, 6),
        WoundModifier(to_wound=1),
    ) == Fraction(1, 9)


def test_negative_modifier_can_make_two_stage_wound_impossible():
    assert get_modified_wound_probability(
        WoundTarget(6, 4),
        WoundModifier(to_wound=-1),
    ) == Fraction(0, 1)