"""Standalone mechanical tests: Tom's Lingering Cold (2024 source)."""
from dataclasses import replace
from fractions import Fraction
import pytest
from three_trolls_lingering_cold import LingeringColdContext, resolve_lingering_cold


def valid():
    return LingeringColdContext("TT_TOM", 3, True, ("enemy1", "enemy2"), "enemy1", 7)


def test_success_spends_one_will():
    result = resolve_lingering_cold(valid())
    assert (result.used, result.will_spent, result.remaining_will) == (True, 1, 2)


def test_success_targets_only_selected_enemy():
    result = resolve_lingering_cold(valid())
    assert result.affected_target_id == "enemy1"


def test_half_is_exact_even_for_odd_fight():
    assert resolve_lingering_cold(valid()).halved_fight_exact == Fraction(7, 2)


def test_even_fight():
    assert resolve_lingering_cold(replace(valid(), target_fight=6)).halved_fight_exact == Fraction(3)


def test_expires_at_end_of_turn():
    assert resolve_lingering_cold(valid()).expires == "end_of_turn"


@pytest.mark.parametrize("changes,reason", [
    ({"actor_profile_id": "TT_BILL"}, "wrong_profile"),
    ({"actor_profile_id": "TT_BERT"}, "wrong_profile"),
    ({"actor_will_available": 0}, "insufficient_will"),
    ({"at_start_of_combat": False}, "wrong_timing"),
    ({"target_id": "unrelated"}, "target_not_engaged"),
    ({"actor_can_use_rule": False}, "rule_unavailable"),
])
def test_rejected_conditions_preserve_resources(changes, reason):
    ctx = replace(valid(), **changes)
    result = resolve_lingering_cold(ctx)
    assert not result.used and result.will_spent == 0
    assert result.remaining_will == ctx.actor_will_available
    assert result.reason == reason and result.halved_fight_exact is None


def test_declining_rule_costs_nothing():
    result = resolve_lingering_cold(valid(), activate=False)
    assert (result.used, result.remaining_will, result.reason) == (False, 3, "not_selected")


def test_zero_fight_is_preserved_as_exact_zero():
    result = resolve_lingering_cold(replace(valid(), target_fight=0))
    assert result.halved_fight_exact == 0


@pytest.mark.parametrize("changes", [
    {"actor_will_available": -1},
    {"actor_will_available": True},
    {"target_fight": -1},
    {"target_fight": 2.5},
    {"target_id": ""},
    {"engaged_enemy_ids": ("a", "a")},
])
def test_invalid_inputs_rejected(changes):
    with pytest.raises(ValueError):
        replace(valid(), **changes)
