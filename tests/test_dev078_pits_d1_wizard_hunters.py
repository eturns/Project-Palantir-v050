"""DEV-078-PITS-D1 Wizard Hunters isolated rule acceptance.

Author: Edward Turns (Project Lead)
"""
from fractions import Fraction
import pytest
from pits_wizard_hunters import calculate_wizard_hunters_strike as strike

DEFAULTS = dict(
    army_list_id="DG_PITS",
    active_army_rule_ids=("DG_WIZARD_HUNTERS",),
    attacker_is_friendly=True, attacker_is_orc=True,
    attacker_is_warrior=True, defender_is_enemy=True,
    defender_can_cast_magical_powers=True, is_melee_strike=True,
    attacker_strength=3, defender_defence=5,
)

def evaluate(**changes):
    return strike(**{**DEFAULTS, **changes})

def test_eligible_orc_warrior_gets_one_bonus():
    r = evaluate()
    assert r.entitled and r.applied_modifier == 1
    assert r.source_rule_id == "DG_WIZARD_HUNTERS"

def test_ordinary_wound_probability_uses_shared_wound_table():
    r = evaluate()
    assert r.baseline_wound_probability == Fraction(1, 3)  # S3 vs D5 = 5+
    assert r.modified_wound_probability == Fraction(1, 2)  # 4+

def test_two_roll_wound_threshold_uses_shared_modifier():
    r = evaluate(attacker_strength=1, defender_defence=7)
    assert r.baseline_wound_probability == Fraction(1, 18) # 6/5
    assert r.modified_wound_probability == Fraction(1, 6)  # 5+ followed by 4+: (2/6)*(3/6)

@pytest.mark.parametrize("changes", [
    {"attacker_is_friendly": False},
    {"attacker_is_orc": False},
    {"attacker_is_warrior": False},
    {"defender_is_enemy": False},
    {"defender_can_cast_magical_powers": False},
    {"is_melee_strike": False},
    {"army_list_id": "DG_ROTN"},
    {"active_army_rule_ids": ()},
])
def test_ineligible_conditions_do_not_apply_bonus(changes):
    r = evaluate(**changes)
    assert not r.entitled
    assert r.applied_modifier == 0
    assert r.source_rule_id is None
    assert r.modified_wound_probability == r.baseline_wound_probability

def test_will_alone_does_not_imply_caster():
    assert not evaluate(defender_can_cast_magical_powers=False).entitled

def test_wound_results_not_calibrated():
    r = evaluate()
    assert r.dashboard_score is None and r.scenario_score is None

@pytest.mark.parametrize("changes", [
    {"attacker_is_orc": 1},
    {"defender_can_cast_magical_powers": None},
    {"is_melee_strike": "yes"},
])
def test_ambiguous_eligibility_rejected(changes):
    with pytest.raises(TypeError):
        evaluate(**changes)

@pytest.mark.parametrize("changes", [
    {"attacker_strength": 0}, {"defender_defence": 11}
])
def test_invalid_statline_rejected(changes):
    with pytest.raises(ValueError):
        evaluate(**changes)
