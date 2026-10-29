"""DEV-077-SMAUG-C2B/E focused defensive branch tests."""
import sys
from fractions import Fraction
from pathlib import Path

import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from defensive_state import DefensiveState
from smaug_breathe_fire import FireVictim, calculate_breathe_fire_evidence
from smaug_fire_defensive_resolution import FireDefender, resolve_breathe_fire_defence


def attack(*victims):
    return calculate_breathe_fire_evidence(
        target_distance_inches=12, primary_target_id="primary", victims=victims)


def test_no_fate_kill_and_ablaze_partition():
    a = attack(FireVictim("primary", defence=5, distance_from_hit_base_inches=0))
    v = resolve_breathe_fire_defence(a, (FireDefender("primary", DefensiveState(20)),)).impacted[0]
    assert v.chance_slain == Fraction(5, 9)
    assert v.chance_set_ablaze == Fraction(5, 18)
    assert v.chance_not_hit_or_immune == Fraction(1, 6)
    assert v.chance_slain + v.chance_set_ablaze + v.chance_not_hit_or_immune == 1


def test_one_fate_prevents_half_of_wounding_hits_even_at_twenty_wounds():
    a = attack(FireVictim("primary", defence=5, distance_from_hit_base_inches=0))
    v = resolve_breathe_fire_defence(a, (FireDefender("primary", DefensiveState(20, 1)),)).impacted[0]
    assert v.chance_wound_prevented == Fraction(5, 18)
    assert v.chance_slain == Fraction(5, 18)
    assert v.chance_set_ablaze == Fraction(5, 9)


def test_two_fate_points_improve_prevention():
    a = attack(FireVictim("primary", defence=5, distance_from_hit_base_inches=0))
    v = resolve_breathe_fire_defence(a, (FireDefender("primary", DefensiveState(3, 2)),)).impacted[0]
    assert v.chance_wound_prevented == Fraction(5, 12)
    assert v.chance_slain == Fraction(5, 36)


def test_immune_model_never_ablaze_and_other_victim_still_resolves():
    a = attack(FireVictim("primary", 5, 0, True), FireVictim("other", 5, 2))
    out = resolve_breathe_fire_defence(a, (
        FireDefender("primary", DefensiveState(10)),
        FireDefender("other", DefensiveState(1)),
    ))
    assert out.attack_count == 1
    assert out.impacted[0].chance_not_hit_or_immune == 1
    assert out.impacted[0].chance_slain == out.impacted[0].chance_set_ablaze == 0
    assert out.impacted[1].chance_slain == Fraction(5, 9)


def test_outside_range_cannot_kill_or_burn():
    a = calculate_breathe_fire_evidence(target_distance_inches=19,
        primary_target_id="primary", victims=(FireVictim("primary", 5, 0),))
    v = resolve_breathe_fire_defence(a, (FireDefender("primary", DefensiveState(1)),)).impacted[0]
    assert v.chance_slain == v.chance_set_ablaze == 0


@pytest.mark.parametrize("defenders", [(), (FireDefender("wrong", DefensiveState(1)),),
    (FireDefender("primary", DefensiveState(1)), FireDefender("primary", DefensiveState(1)))])
def test_missing_foreign_and_duplicate_defensive_states_rejected(defenders):
    a = attack(FireVictim("primary", 5, 0))
    with pytest.raises(ValueError):
        resolve_breathe_fire_defence(a, defenders)


def test_will_as_fate_not_silently_ignored():
    with pytest.raises(ValueError, match="Will-as-Fate"):
        FireDefender("primary", DefensiveState(1, 0, 2))


def test_might_can_help_fate():
    a = attack(FireVictim("primary", 5, 0))
    v = resolve_breathe_fire_defence(a, (
        FireDefender("primary", DefensiveState(1, 1), might_for_fate=1),)).impacted[0]
    assert v.chance_wound_prevented == Fraction(10, 27)
