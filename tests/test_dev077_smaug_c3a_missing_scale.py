"""DEV-077-SMAUG-C3A/E: exact Missing Scale bounded shot tests."""
from fractions import Fraction
import pytest
from defensive_state import DefensiveState
from smaug_missing_scale import calculate_missing_scale_evidence as calculate


def test_strength_three_versus_defence_nine():
    result = calculate(shooter_shoot_value="4+", missile_strength=3)
    # S3 vs D9 needs 6/5 (2/36); ordinary hit faces 4,5.
    assert result.ordinary_wound_probability == Fraction(2, 6) * Fraction(2, 36)
    assert result.missing_scale_wound_probability == Fraction(1, 6) * Fraction(2, 36)
    assert result.expected_incoming_wounds == Fraction(5, 6) * Fraction(2, 36)
    assert result.elimination_probability == 0


def test_modified_six_does_not_become_a_natural_six():
    result = calculate(shooter_shoot_value="4+", missile_strength=3, to_hit_modifier=1)
    # 3, 4, 5 are ordinary hits; only original 6 is special.
    assert result.ordinary_wound_probability == Fraction(3, 6) * Fraction(2, 36)
    assert result.missing_scale_wound_probability == Fraction(1, 6) * Fraction(2, 36)


def test_natural_six_can_fail_when_penalty_large():
    result = calculate(shooter_shoot_value="6+", missile_strength=4, to_hit_modifier=-1)
    assert result.missing_scale_wound_probability == 0
    assert result.expected_incoming_wounds == 0


def test_elimination_uses_all_missile_strength_wounds():
    result = calculate(
        shooter_shoot_value="2+", missile_strength=3,
        smaug_state=DefensiveState(2, 0),
    )
    assert result.elimination_probability == result.missing_scale_wound_probability


def test_fate_prevents_kill_probability_not_wound_generation():
    without = calculate(shooter_shoot_value="2+", missile_strength=3,
                        smaug_state=DefensiveState(2, 0))
    with_fate = calculate(shooter_shoot_value="2+", missile_strength=3,
                          smaug_state=DefensiveState(2, 2))
    assert with_fate.expected_incoming_wounds == without.expected_incoming_wounds
    assert with_fate.elimination_probability < without.elimination_probability


def test_probabilities_partition_and_no_mutation():
    state = DefensiveState(20, 0)
    result = calculate(shooter_shoot_value="4+", missile_strength=3, smaug_state=state)
    assert sum((result.ordinary_wound_probability,
                result.missing_scale_wound_probability,
                result.miss_or_no_wound_probability)) == 1
    assert state == DefensiveState(20, 0)


@pytest.mark.parametrize("strength", [0, 11, 3.5, True])
def test_invalid_missile_strength_rejected(strength):
    with pytest.raises(ValueError):
        calculate(shooter_shoot_value="4+", missile_strength=strength)


def test_will_as_fate_not_silently_ignored():
    with pytest.raises(ValueError, match="Will-as-Fate"):
        calculate(shooter_shoot_value="4+", missile_strength=3,
                  smaug_state=DefensiveState(20, 0, 1))
