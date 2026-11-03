"""DEV-078-GT-C1 Strength in Numbers acceptance.
Author: Edward Turns (Project Lead).
"""
from dataclasses import replace
from fractions import Fraction
import pytest

from loader import load_all_profiles
from configured_profile import ConfiguredProfile
from courage_test import CourageTestContext
from goblin_town_strength_in_numbers import (
    RULE_ID, StrengthInNumbersContext, assess_strength_in_numbers,
)


@pytest.fixture(scope="module")
def profiles():
    return {p.id: ConfiguredProfile(p) for p in load_all_profiles()}


def ctx(**overrides):
    values=dict(army_list_id="GOBLIN_TOWN",active_army_rule_ids=(RULE_ID,),
                army_broken=False,friendly_model=True,is_terror_charge_test=True)
    values.update(overrides)
    return StrengthInNumbersContext(**values)


def test_qualifying_goblin_receives_plus_one(profiles):
    ev=assess_strength_in_numbers(profiles["GT_WARRIOR"],ctx())
    assert ev.entitled and ev.bonus==1
    assert ev.modified_modifier==1 and ev.modified_probability>=ev.ordinary_probability


@pytest.mark.parametrize("id",["GT_WARRIOR","GT_CAPTAIN","GT_KING","GT_GRINNAH"])
def test_all_goblin_types_eligible(profiles,id):
    assert assess_strength_in_numbers(profiles[id],ctx()).entitled


@pytest.mark.parametrize("changes",[
    {"army_broken":True},
    {"friendly_model":False},
    {"is_terror_charge_test":False},
    {"army_list_id":"GUNDABAD"},
    {"active_army_rule_ids":()},
])
def test_non_qualifying_conditions_do_not_grant_bonus(profiles,changes):
    ev=assess_strength_in_numbers(profiles["GT_WARRIOR"],ctx(**changes))
    assert not ev.entitled and ev.bonus==0
    assert ev.modified_probability==ev.ordinary_probability


def test_gollum_is_not_goblin(profiles):
    ev=assess_strength_in_numbers(profiles["GT_GOLLUM"],ctx())
    assert not ev.entitled


def test_existing_modifier_preserved_and_increased(profiles):
    c=ctx(base_courage_context=CourageTestContext(roll_modifier=-2))
    ev=assess_strength_in_numbers(profiles["GT_WARRIOR"],c)
    assert ev.base_modifier==-2 and ev.modified_modifier==-1


def test_automatic_success_not_removed(profiles):
    c=ctx(base_courage_context=CourageTestContext(automatically_passes=True))
    ev=assess_strength_in_numbers(profiles["GT_WARRIOR"],c)
    assert ev.ordinary_probability==Fraction(1) and ev.modified_probability==Fraction(1)


def test_no_score_or_calibration_output(profiles):
    ev=assess_strength_in_numbers(profiles["GT_WARRIOR"],ctx())
    assert ev.dashboard_score is None and ev.scenario_score is None


@pytest.mark.parametrize("key",["army_broken","friendly_model","is_terror_charge_test"])
def test_strict_booleans(key):
    with pytest.raises(TypeError):
        ctx(**{key:1})


@pytest.mark.parametrize("bad",[True,1.5,"1"])
def test_invalid_base_modifier(bad):
    with pytest.raises(TypeError):
        ctx(base_courage_context=CourageTestContext(roll_modifier=bad))


def test_not_configured_profile_rejected():
    with pytest.raises(TypeError):
        assess_strength_in_numbers(object(),ctx())
