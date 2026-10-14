"""DEV-077S-I2-G2-D4B3 rules-backed conditional outcome tests."""
from fractions import Fraction
import pytest
from hero_hunting_remaining_spells import (
    calculate_curse_hero_hunting, calculate_drain_courage_hero_hunting,
    calculate_fog_of_disarray_hero_hunting, calculate_instil_fear_hero_hunting,
    calculate_your_staff_is_broken_hero_hunting,
)

P = Fraction(2, 3)


def test_curse_reduces_fate_without_claiming_kill():
    out = calculate_curse_hero_hunting(effect_probability=P, target_remaining_fate=2)
    assert out.remaining_fate_on_effect == 1
    assert out.direct_elimination_probability == 0


def test_curse_does_not_create_negative_fate():
    assert calculate_curse_hero_hunting(effect_probability=P, target_remaining_fate=0).remaining_fate_on_effect == 0


def test_curse_mount_part_is_explicit():
    assert calculate_curse_hero_hunting(effect_probability=P, target_remaining_fate=1, target_part="mount").remaining_fate_on_effect == 0


def test_curse_rejects_unknown_cavalry_part():
    with pytest.raises(ValueError, match="target part"):
        calculate_curse_hero_hunting(effect_probability=P, target_remaining_fate=1, target_part="cavalry")


def test_drain_courage_worsens_required_roll():
    out = calculate_drain_courage_hero_hunting(effect_probability=P, target_courage_required_roll=5)
    assert out.courage_target_on_effect == 6
    assert out.duration == "persistent_remainder_of_game"


def test_drain_courage_can_reach_seven_plus():
    assert calculate_drain_courage_hero_hunting(effect_probability=P, target_courage_required_roll=6).courage_target_on_effect == 7


def test_drain_courage_saturates_at_seven_plus():
    assert calculate_drain_courage_hero_hunting(effect_probability=P, target_courage_required_roll=7).courage_target_on_effect == 7


def test_fog_uses_self_area_and_exhaustion():
    out = calculate_fog_of_disarray_hero_hunting(effect_probability=P)
    assert (out.intelligence_area_inches, out.intelligence_test_modifier_on_effect) == (6, -1)
    assert out.duration == "exhaustion"
    assert out.direct_elimination_probability == 0


def test_instil_fear_temporary_area():
    out = calculate_instil_fear_hero_hunting(effect_probability=P)
    assert out.fearful_area_inches == 6
    assert out.gains_fearful_on_effect
    assert out.duration == "temporary_until_end_phase"


def test_staff_removal_only_on_qualifying_target():
    out = calculate_your_staff_is_broken_hero_hunting(effect_probability=P, target_has_staff_of_power=True)
    assert out.staff_destroyed_on_effect
    assert out.direct_elimination_probability == 0


def test_staff_without_power_fails_closed():
    with pytest.raises(ValueError, match="Staff of Power"):
        calculate_your_staff_is_broken_hero_hunting(effect_probability=P, target_has_staff_of_power=False)


@pytest.mark.parametrize("p", [Fraction(-1, 10), Fraction(11, 10), 0.5, None])
def test_invalid_probabilities_fail_closed(p):
    with pytest.raises(ValueError, match="effect_probability"):
        calculate_instil_fear_hero_hunting(effect_probability=p)


def test_boolean_resource_rejected():
    with pytest.raises(ValueError, match="nonnegative integer"):
        calculate_curse_hero_hunting(effect_probability=P, target_remaining_fate=True)


def test_drain_courage_invalid_target_rejected():
    with pytest.raises(ValueError, match="2..7"):
        calculate_drain_courage_hero_hunting(effect_probability=P, target_courage_required_roll=8)
