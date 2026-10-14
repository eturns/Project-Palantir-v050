from fractions import Fraction
import pytest
from hero_hunting_control_spells import (
    calculate_transfix_hero_hunting, calculate_compel_hero_hunting,
)


def test_transfix_blocks_activation():
    assert calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2)).activation_blocked


def test_transfix_blocks_shooting_and_heroic_actions():
    x = calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2))
    assert x.shooting_blocked and x.heroic_actions_blocked


def test_transfix_blocks_active_abilities():
    assert calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2)).active_abilities_blocked


def test_transfix_blocks_winning_strikes_not_the_duel():
    x = calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2))
    assert x.strikes_when_winning_duel_blocked
    assert x.compelled_max_movement_inches is None


def test_transfix_expires_end_phase():
    assert calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2)).duration == "temporary_until_end_phase"


def test_compel_half_move():
    x = calculate_compel_hero_hunting(effect_probability=Fraction(1, 3), target_move_inches=6)
    assert x.compelled_max_movement_inches == 3


def test_compel_fractional_half_move():
    x = calculate_compel_hero_hunting(effect_probability=Fraction(1, 3), target_move_inches=5)
    assert x.compelled_max_movement_inches == Fraction(5, 2)


def test_compel_prevents_further_movement_after_moved():
    x = calculate_compel_hero_hunting(effect_probability=Fraction(1, 3), target_move_inches=6)
    assert x.further_movement_blocked and not x.activation_blocked


def test_compel_does_not_forbid_heroics_shooting_and_strikes():
    x = calculate_compel_hero_hunting(effect_probability=Fraction(1, 3), target_move_inches=6)
    assert not (x.heroic_actions_blocked or x.shooting_blocked or x.strikes_when_winning_duel_blocked)


def test_engaged_target_cannot_be_pulled_out_of_combat():
    x = calculate_compel_hero_hunting(effect_probability=Fraction(1, 3), target_move_inches=6, target_engaged_in_combat=True)
    assert x.compelled_max_movement_inches == 0
    assert x.evidence_status == "engaged_target_cannot_be_moved_out_of_combat"


def test_no_direct_elimination_for_either_spell():
    x = calculate_transfix_hero_hunting(effect_probability=Fraction(1, 2))
    y = calculate_compel_hero_hunting(effect_probability=Fraction(1, 2), target_move_inches=6)
    assert x.direct_elimination_probability is None and y.direct_elimination_probability is None


@pytest.mark.parametrize("value", [Fraction(-1, 4), Fraction(5, 4), 0.5])
def test_effect_probability_fail_closed(value):
    with pytest.raises(ValueError, match="effect_probability"):
        calculate_transfix_hero_hunting(effect_probability=value)


@pytest.mark.parametrize("value", [-1, 1.5, True])
def test_compel_invalid_move_value_rejected(value):
    with pytest.raises(ValueError, match="target_move_inches"):
        calculate_compel_hero_hunting(effect_probability=Fraction(1, 2), target_move_inches=value)
