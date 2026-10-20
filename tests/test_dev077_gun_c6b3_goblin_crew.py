"""DEV-077-GUN-C6-B3: Goblin Crew focused tests."""
from fractions import Fraction
from types import SimpleNamespace as NS
import pytest

from gundabad_goblin_crew import (
    GoblinCrewCombatContext, is_gundabad_catapult_troll,
    can_make_goblin_crew_strikes, resolve_goblin_crew_strikes,
    expected_goblin_crew_strikes,
)


def model(profile_id="GUNDABAD_CATAPULT_TROLL"):
    return NS(profile=NS(id=profile_id), effective_strength=8)


def context(**overrides):
    args = dict(combat_won=True, troll_strikes_resolved=True)
    args.update(overrides)
    return GoblinCrewCombatContext(**args)


def test_correct_profile():
    assert is_gundabad_catapult_troll(model())


def test_other_profile_cannot_use_rule():
    assert not can_make_goblin_crew_strikes(model("TROLL_BRUTE"), context())


def test_lost_combat_no_strikes():
    assert not can_make_goblin_crew_strikes(model(), context(combat_won=False))


def test_must_follow_troll_strikes():
    assert not can_make_goblin_crew_strikes(model(), context(troll_strikes_resolved=False))


def test_ending_brutal_power_attack_prevents_strikes():
    assert not can_make_goblin_crew_strikes(model(), context(combat_ended_by_brutal_power_attack=True))


def test_crew_unavailable_prevents_strikes():
    assert not can_make_goblin_crew_strikes(model(), context(crew_able_to_act=False))


def test_valid_crew_strikes_are_strength_three():
    result = resolve_goblin_crew_strikes(model(), context(), d6_strikes=4, target_defence=4)
    assert result.strength == 3 and result.strikes == 4


def test_shared_wound_probability():
    result = resolve_goblin_crew_strikes(model(), context(), d6_strikes=2, target_defence=4)
    assert result.wound_probability_per_strike == Fraction(1, 3)
    assert result.expected_wounds == Fraction(2, 3)


def test_wound_distribution_normalised():
    result = resolve_goblin_crew_strikes(model(), context(), d6_strikes=6, target_defence=7)
    assert len(result.wound_count_distribution) == 7
    assert sum(result.wound_count_distribution) == 1


def test_expected_d6_count():
    assert expected_goblin_crew_strikes(model(), context()) == Fraction(7, 2)


def test_disabled_expected_count():
    assert expected_goblin_crew_strikes(model(), context(combat_won=False)) == 0


@pytest.mark.parametrize("roll", [0, 7, True, 2.5])
def test_reject_bad_d6(roll):
    with pytest.raises(ValueError):
        resolve_goblin_crew_strikes(model(), context(), d6_strikes=roll, target_defence=4)


@pytest.mark.parametrize("defence", [0, 11, True])
def test_reject_bad_defence(defence):
    with pytest.raises(ValueError):
        resolve_goblin_crew_strikes(model(), context(), d6_strikes=2, target_defence=defence)


def test_reject_without_permission():
    with pytest.raises(ValueError):
        resolve_goblin_crew_strikes(model(), context(combat_won=False), d6_strikes=2, target_defence=4)


def test_context_type_rejected():
    with pytest.raises(TypeError):
        can_make_goblin_crew_strikes(model(), None)


def test_no_strength_eight_or_ten_leakage():
    result = resolve_goblin_crew_strikes(model(), context(), d6_strikes=1, target_defence=10)
    assert result.strength == 3
    assert result.wound_probability_per_strike == Fraction(1, 36)
