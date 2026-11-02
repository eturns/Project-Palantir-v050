"""DEV-078-AH-C1 standalone acceptance. Edward Turns (Project Lead)."""
from fractions import Fraction
from types import SimpleNamespace
import pytest
from configured_profile import ConfiguredProfile
from profiles import Profile
from pale_orcs_demands import calculate_pale_orcs_demands

@pytest.fixture
def combatant():
    return ConfiguredProfile(Profile(
        id="AH_TEST_ORC", name="Test Orc", points=8, movement=6,
        fight=3, shooting="5+", strength=4, defence=4,
        attacks=1, wounds=1, courage="7+", intelligence="8+",
        might=0, will=0, fate=0, max_in_army=100
    ))

@pytest.fixture
def args(combatant):
    return dict(combatant=combatant, army_list_id="AZOGS_HUNTERS",
        active_army_rule_ids=("DG_PALE_ORCS_DEMANDS",),
        is_friendly_orc_warrior=True, charging_enemy_with_terror=True,
        nearest_friendly_hero_distance_inches=6)

def evaluate(args, **updates):
    return calculate_pale_orcs_demands(**{**args,**updates})

def test_six_inches_is_eligible(args):
    e=evaluate(args)
    assert e.entitled and e.bonus==1
    assert e.source_rule_id=="DG_PALE_ORCS_DEMANDS"

def test_actual_2d6_probabilities(args):
    e=evaluate(args)
    assert e.baseline_pass_probability==Fraction(21,36)
    assert e.modified_pass_probability==Fraction(26,36)

@pytest.mark.parametrize("updates",[
    {"nearest_friendly_hero_distance_inches":6.0001},
    {"nearest_friendly_hero_distance_inches":None},
    {"is_friendly_orc_warrior":False},
    {"charging_enemy_with_terror":False},
    {"army_list_id":"DG_PITS"},
    {"active_army_rule_ids":()},
])
def test_ineligible_has_no_bonus(args,updates):
    e=evaluate(args,**updates)
    assert not e.entitled and e.bonus==0
    assert e.modified_pass_probability==e.baseline_pass_probability

def test_stacks_with_explicit_other_modifier(args):
    e=evaluate(args,other_courage_roll_modifier=-1)
    assert e.baseline_pass_probability==Fraction(15,36)
    assert e.modified_pass_probability==Fraction(21,36)

@pytest.mark.parametrize("invalid",[-1,float("inf"),float("nan"),True,"5"])
def test_invalid_distance_rejected(args,invalid):
    with pytest.raises(ValueError):
        evaluate(args,nearest_friendly_hero_distance_inches=invalid)

@pytest.mark.parametrize("updates",[
    {"is_friendly_orc_warrior":None},
    {"charging_enemy_with_terror":1},
    {"other_courage_roll_modifier":0.5},
    {"active_army_rule_ids":["DG_PALE_ORCS_DEMANDS"]},
])
def test_ambiguous_inputs_rejected(args,updates):
    with pytest.raises(TypeError):
        evaluate(args,**updates)

def test_no_dashboard_or_scenario_scoring(args):
    e=evaluate(args)
    assert e.dashboard_score is None and e.scenario_score is None
