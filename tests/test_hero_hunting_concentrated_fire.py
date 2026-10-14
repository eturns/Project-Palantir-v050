from fractions import Fraction
from types import SimpleNamespace

import pytest

from defensive_state import DefensiveState
from shooting_eligibility import ShootingContext
from ranged_weapon_profile import RangedWeaponProfile
from hero_hunting_concentrated_fire import (
    FocusedShooter, calculate_concentrated_fire_evidence,
)
from hero_hunting_shooting import calculate_hero_hunting_shooting_evidence


def profile(*, shoot="4+", defence=4, rules=()):
    weapon = SimpleNamespace(id="WG_ORC_BOW", special_rules=())
    return SimpleNamespace(
        effective_wargear=(weapon,), effective_shooting=shoot,
        effective_defence=defence,
        effective_special_rules=tuple(SimpleNamespace(rule=SimpleNamespace(id=r)) for r in rules),
        profile=SimpleNamespace(keywords=()),
    )


def shooter(id, *, distance=12, shoot="4+", rules=(), los=True):
    return FocusedShooter(
        shooter_id=id,
        attacker=profile(shoot=shoot, rules=rules),
        weapon=RangedWeaponProfile("WG_ORC_BOW", 18, 2, 1),
        context=ShootingContext(target_distance_inches=distance),
        clear_line_of_sight=los,
    )


def evaluate(*shooters, wounds=1, fate=0):
    return calculate_concentrated_fire_evidence(
        shooters=shooters, defender=profile(),
        defender_state=DefensiveState(wounds, remaining_fate=fate),
    )


def test_single_shooter_parity_with_c1():
    s = shooter("a")
    state = DefensiveState(2, remaining_fate=1)
    aggregate = calculate_concentrated_fire_evidence(
        shooters=(s,), defender=profile(), defender_state=state
    )
    individual = calculate_hero_hunting_shooting_evidence(
        attacker=s.attacker, defender=profile(), weapon=s.weapon,
        defender_state=state, context=s.context, clear_line_of_sight=True,
    )
    assert aggregate.elimination_probability == individual.elimination_probability
    assert aggregate.expected_wounds == individual.expected_wounds


def test_two_shooters_elimination_combines_before_fate():
    a = evaluate(shooter("a"), shooter("b"))
    p = a.expected_wounds / 2
    assert a.total_shots == 2
    assert a.elimination_probability == 1 - (1-p)**2
    assert sum(a.incoming_wound_distribution) == 1


def test_two_wound_hero_needs_two_successes():
    a = evaluate(shooter("a"), shooter("b"), wounds=2)
    p = a.expected_wounds / 2
    assert a.elimination_probability == p**2


def test_mixed_shooters_and_expert_shot():
    a = evaluate(shooter("a",rules=("EXPERT_SHOT",)), shooter("b",shoot="5+"))
    assert a.total_shots == 3
    assert a.shooter_count == 2
    assert sum(a.incoming_wound_distribution) == 1


def test_shared_fate_uses_joint_wound_distribution():
    without = evaluate(shooter("a"), shooter("b"), fate=0)
    with_fate = evaluate(shooter("a"), shooter("b"), fate=1)
    assert with_fate.elimination_probability < without.elimination_probability


def test_duplicate_identity_rejected():
    with pytest.raises(ValueError, match="duplicated shooter"):
        evaluate(shooter("a"), shooter("a"))


@pytest.mark.parametrize("bad", [shooter("x",distance=30),shooter("x",los=False)])
def test_ineligible_shooter_does_not_silently_disappear(bad):
    with pytest.raises(ValueError, match="Incomplete Hero Hunting"):
        evaluate(shooter("a"), bad)


def test_missing_shooters_rejected():
    with pytest.raises(ValueError, match="at least one shooter"):
        evaluate()
