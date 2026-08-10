from fractions import Fraction

from resurrection_probability import (
    get_resurrection_probability_with_master_of_the_nazgul,
    get_resurrection_probability_with_necromancer_will,
    get_resurrection_probability_with_resource_state,
    get_resurrection_success_probability,
)
from hero_resource_state import HeroResourceState
import pytest

def test_standard_unholy_resurrection_succeeds_two_thirds_of_the_time():
    result = get_resurrection_success_probability()

    assert result == Fraction(2, 3)


def test_resurrection_probability_supports_easier_target():
    result = get_resurrection_success_probability(
        required_roll=3,
    )

    assert result == Fraction(2, 3)


def test_resurrection_probability_supports_harder_target():
    result = get_resurrection_success_probability(
        required_roll=5,
    )

    assert result == Fraction(1, 3)


def test_resurrection_probability_is_certain_at_one_plus():
    result = get_resurrection_success_probability(
        required_roll=1,
    )

    assert result == Fraction(1, 1)


def test_resurrection_probability_is_impossible_above_six():
    result = get_resurrection_success_probability(
        required_roll=7,
    )

    assert result == Fraction(0, 1)

def test_plus_one_modifier_improves_standard_resurrection():
    result = get_resurrection_success_probability(
        roll_modifier=1,
    )

    assert result == Fraction(5, 6)


def test_minus_one_modifier_reduces_standard_resurrection():
    result = get_resurrection_success_probability(
        roll_modifier=-1,
    )

    assert result == Fraction(1, 2)


def test_large_positive_modifier_can_make_resurrection_certain():
    result = get_resurrection_success_probability(
        roll_modifier=5,
    )

    assert result == Fraction(1, 1)


def test_large_negative_modifier_can_make_resurrection_impossible():
    result = get_resurrection_success_probability(
        roll_modifier=-6,
    )

    assert result == Fraction(0, 1)

def test_master_of_the_nazgul_improves_in_range_resurrection():
    result = (
        get_resurrection_probability_with_master_of_the_nazgul(
            necromancer_remaining_will=20,
            distance_inches=18,
        )
    )

    assert result == Fraction(5, 6)


def test_master_of_the_nazgul_does_not_help_outside_range():
    result = (
        get_resurrection_probability_with_master_of_the_nazgul(
            necromancer_remaining_will=20,
            distance_inches=18.1,
        )
    )

    assert result == Fraction(2, 3)


def test_master_bonus_combines_with_other_roll_modifier():
    result = (
        get_resurrection_probability_with_master_of_the_nazgul(
            necromancer_remaining_will=20,
            distance_inches=18,
            additional_roll_modifier=-1,
        )
    )

    assert result == Fraction(2, 3)

def test_one_necromancer_will_can_make_in_range_resurrection_certain():
    result = (
        get_resurrection_probability_with_necromancer_will(
            necromancer_remaining_will=20,
            distance_inches=18,
            will_points_available_to_spend=1,
        )
    )

    assert result == Fraction(1, 1)


def test_necromancer_cannot_spend_will_outside_master_range():
    result = (
        get_resurrection_probability_with_necromancer_will(
            necromancer_remaining_will=20,
            distance_inches=18.1,
            will_points_available_to_spend=5,
        )
    )

    assert result == Fraction(2, 3)


def test_necromancer_will_can_offset_elven_or_magical_penalty():
    result = (
        get_resurrection_probability_with_necromancer_will(
            necromancer_remaining_will=20,
            distance_inches=18,
            will_points_available_to_spend=1,
            additional_roll_modifier=-1,
        )
    )

    assert result == Fraction(5, 6)


def test_resurrection_cannot_spend_more_will_than_necromancer_has():
    with pytest.raises(
        ValueError,
        match=(
            "Cannot spend more Will than the "
            "Necromancer has remaining."
        ),
    ):
        get_resurrection_probability_with_necromancer_will(
            necromancer_remaining_will=1,
            distance_inches=6,
            will_points_available_to_spend=2,
        )

def test_resurrection_probability_uses_hero_resource_state():
    resources = HeroResourceState(
        remaining_might=0,
        remaining_will=20,
        remaining_fate=0,
    )

    result = get_resurrection_probability_with_resource_state(
        necromancer_resources=resources,
        distance_inches=18,
        will_points_available_to_spend=1,
    )

    assert result == Fraction(1, 1)