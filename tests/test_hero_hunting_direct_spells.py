"""DEV-077S-I2-G2-D4B1 focused rules-backed effects."""
from fractions import Fraction
import pytest

from hero_hunting_direct_spells import (
    calculate_chill_soul_hero_hunting,
    calculate_wither_hero_hunting,
)


def test_chill_soul_causes_one_wound_without_strength_hit():
    result = calculate_chill_soul_hero_hunting(
        effect_probability=Fraction(1, 3), target_remaining_wounds=2,
    )
    assert result.conditional_wounds == 1
    assert result.target_elimination_probability == 0
    assert result.resulting_strength is None


def test_chill_soul_one_wound_no_prevention_stays_unresolved():
    result = calculate_chill_soul_hero_hunting(
        effect_probability=Fraction(1, 2), target_remaining_wounds=1,
    )
    assert result.target_elimination_probability is None
    assert result.evidence_status == "defensive_prevention_unresolved"


def test_chill_soul_conditional_fate_prevention_is_applied_once():
    result = calculate_chill_soul_hero_hunting(
        effect_probability=Fraction(3, 5), target_remaining_wounds=1,
        conditional_wound_not_prevented_probability=Fraction(1, 3),
    )
    assert result.target_elimination_probability == Fraction(1, 5)


def test_chill_soul_prevention_certain_means_no_elimination():
    result = calculate_chill_soul_hero_hunting(
        effect_probability=Fraction(1), target_remaining_wounds=1,
        conditional_wound_not_prevented_probability=Fraction(0),
    )
    assert result.target_elimination_probability == 0


def test_wither_reduces_strength_without_immediate_kill():
    result = calculate_wither_hero_hunting(
        effect_probability=Fraction(2, 3), target_current_strength=3,
    )
    assert result.resulting_strength == 2
    assert result.conditional_wounds == 0
    assert result.target_elimination_probability == 0


def test_wither_strength_one_eliminates_chosen_model():
    result = calculate_wither_hero_hunting(
        effect_probability=Fraction(2, 3), target_current_strength=1,
    )
    assert result.resulting_strength == 0
    assert result.target_elimination_probability == Fraction(2, 3)


def test_wither_mount_elimination_not_counted_as_hero_elimination():
    result = calculate_wither_hero_hunting(
        effect_probability=Fraction(1, 2), target_current_strength=1,
        target_part="mount",
    )
    assert result.evidence_status == "chosen_part_eliminated_not_necessarily_hero"
    assert result.target_elimination_probability is None


@pytest.mark.parametrize("value", [-1, 0, True, 1.2])
def test_invalid_strength_rejected(value):
    with pytest.raises(ValueError, match="positive integer"):
        calculate_wither_hero_hunting(
            effect_probability=Fraction(1, 2), target_current_strength=value,
        )


def test_invalid_target_part_fails_closed():
    with pytest.raises(ValueError, match="explicit"):
        calculate_wither_hero_hunting(
            effect_probability=Fraction(1, 2), target_current_strength=2,
            target_part="cavalry_unspecified",
        )


def test_probability_outside_unit_interval_rejected():
    with pytest.raises(ValueError, match="Fraction"):
        calculate_chill_soul_hero_hunting(
            effect_probability=Fraction(3, 2), target_remaining_wounds=1,
        )
