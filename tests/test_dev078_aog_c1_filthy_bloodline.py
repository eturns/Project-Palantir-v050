"""DEV-078-AoG-C1 standalone acceptance. Edward Turns (Project Lead)."""
from fractions import Fraction
import pytest

from gundabad_filthy_bloodline import calculate_filthy_bloodline_strike

BASE = dict(
    army_list_id="GUNDABAD",
    active_army_rule_ids=("GUNDABAD_FILTHY_BLOODLINE",),
    attacker_profile_id="AZOG_THE_DEFILER",
    attacker_is_friendly=True,
    defender_is_erebor=True,
    defender_is_enemy=True,
    is_melee_strike=True,
    attacker_strength=5,
    defender_defence=3,
)


def evaluate(**updates):
    return calculate_filthy_bloodline_strike(**{**BASE, **updates})


def test_azog_striking_erebor_gets_reroll():
    evidence = evaluate()
    assert evidence.entitled
    assert evidence.reroll_failed_to_wound
    assert evidence.source_rule_id == "GUNDABAD_FILTHY_BLOODLINE"


def test_ordinary_wound_probability_is_exact():
    evidence = evaluate()
    assert evidence.baseline_wound_probability == Fraction(2, 3)  # S5 vs D3: 3+
    assert evidence.modified_wound_probability == Fraction(8, 9)


def test_two_roll_high_defence_reuses_shared_reroll_engine():
    evidence = evaluate(attacker_strength=3, defender_defence=8)
    assert evidence.baseline_wound_probability == Fraction(1, 12)  # 6/4+
    assert evidence.modified_wound_probability == Fraction(11, 48)


@pytest.mark.parametrize("updates", [
    {"army_list_id": "AZOGS_HUNTERS"},
    {"active_army_rule_ids": ()},
    {"attacker_profile_id": "BOLG_SPAWN_OF_AZOG"},
    {"attacker_is_friendly": False},
    {"defender_is_erebor": False},
    {"defender_is_enemy": False},
    {"is_melee_strike": False},
])
def test_nonqualifying_attacks_remain_unchanged(updates):
    evidence = evaluate(**updates)
    assert not evidence.entitled
    assert evidence.modified_wound_probability == evidence.baseline_wound_probability
    assert evidence.source_rule_id is None


@pytest.mark.parametrize("updates", [
    {"attacker_is_friendly": 1},
    {"defender_is_erebor": None},
    {"defender_is_enemy": "yes"},
    {"is_melee_strike": 0},
    {"active_army_rule_ids": ["GUNDABAD_FILTHY_BLOODLINE"]},
])
def test_ambiguous_context_rejected(updates):
    with pytest.raises(TypeError):
        evaluate(**updates)


@pytest.mark.parametrize("updates", [
    {"attacker_strength": 0},
    {"defender_defence": 11},
])
def test_invalid_profile_characteristics_rejected(updates):
    with pytest.raises(ValueError):
        evaluate(**updates)


def test_no_dashboard_or_scenario_scores():
    evidence = evaluate()
    assert evidence.dashboard_score is None
    assert evidence.scenario_score is None
