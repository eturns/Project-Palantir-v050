"""Crushing Club must not break generic hero-hunting evidence objects."""
from types import SimpleNamespace

from gundabad_crushing_club import (
    crushing_club_knockdown,
    crushing_club_strike_damage,
    uses_crushing_club,
)
from special_rule_strike_damage import get_special_rule_strike_damage


def test_combat_only_attacker_without_profile_has_no_club_effect():
    attacker = SimpleNamespace(
        effective_attacks=1,
        effective_fight=3,
        effective_special_rules=(),
        effective_wargear=(),
    )
    assert uses_crushing_club(attacker) is False
    assert crushing_club_strike_damage(attacker) is None
    assert get_special_rule_strike_damage(attacker).wounds_per_successful_strike == 1
    assert crushing_club_knockdown(attacker, struck=True, slain=False).resolve(6) is False


def test_unrelated_profile_and_partial_wargear_object_are_ignored():
    attacker = SimpleNamespace(
        profile=SimpleNamespace(id="GUNDABAD_ORC_CAPTAIN"),
        effective_special_rules=(),
        effective_wargear=(SimpleNamespace(name="hand weapon"),),
    )
    assert uses_crushing_club(attacker) is False
    assert get_special_rule_strike_damage(attacker).wounds_per_successful_strike == 1
