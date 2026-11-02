"""DEV-078-AoG-D1 standalone Horn acceptance. Author: Edward Turns (Project Lead)."""
from dataclasses import replace
from fractions import Fraction
import pytest

from gundabad_horn_of_gorgoroth import (
    ARMY_LIST_ID, RULE_ID, HornState, HornActivation, activate_horn,
    advance_turn, horn_active, horn_courage_modifier, courage_probability_with_horn
)


def request(**kwargs):
    defaults = dict(army_list_id=ARMY_LIST_ID, active_army_rule_ids=(RULE_ID,),
                    general_alive=True, general_on_battlefield=True,
                    priority_determined=True, activate=True)
    defaults.update(kwargs)
    return HornActivation(**defaults)


def active_state():
    return activate_horn(HornState(), request()).state


def test_initial_unused():
    assert not HornState().used


def test_activation_succeeds():
    x=activate_horn(HornState(),request())
    assert x.activated and x.status=='activated' and horn_active(x.state)


def test_declaration_is_optional():
    assert activate_horn(HornState(),request(activate=False)).status=='not_declared'


@pytest.mark.parametrize('change,status', [
    ({'army_list_id':'DG_PITS'},'not_entitled'),
    ({'active_army_rule_ids':()},'not_entitled'),
    ({'general_alive':False},'general_unavailable'),
    ({'general_on_battlefield':False},'general_unavailable'),
    ({'priority_determined':False},'priority_not_determined'),
])
def test_activation_guard(change,status):
    assert activate_horn(HornState(),request(**change)).status==status


def test_cannot_activate_twice():
    assert activate_horn(active_state(),request()).status=='already_used'


def test_cannot_activate_in_future_turn():
    assert activate_horn(advance_turn(active_state()),request()).status=='already_used'


def test_effect_expires_after_turn():
    assert not horn_active(advance_turn(active_state()))


def test_usage_persists_after_turn():
    assert advance_turn(active_state()).used


def test_friendly_bonus():
    assert horn_courage_modifier(active_state(),friendly_gundabad=True)==2


def test_enemy_penalty():
    assert horn_courage_modifier(active_state(),enemy=True)==-2


def test_effect_inactive_other_models():
    assert horn_courage_modifier(active_state())==0


def test_inactive_returns_no_friendly_bonus():
    assert horn_courage_modifier(HornState(),friendly_gundabad=True)==0


def test_inactive_preserves_other_enemy_penalty():
    assert horn_courage_modifier(HornState(),enemy=True,existing_enemy_penalty=-1)==-1


@pytest.mark.parametrize('existing,expected',[(-1,-2),(-2,-2),(-3,-3),(-4,-4)])
def test_enemy_penalties_do_not_stack(existing,expected):
    assert horn_courage_modifier(active_state(),enemy=True,existing_enemy_penalty=existing)==expected


def test_conflicting_relationships_rejected():
    with pytest.raises(ValueError):
        horn_courage_modifier(active_state(),friendly_gundabad=True,enemy=True)


def test_invalid_priority_type_rejected():
    with pytest.raises(TypeError):
        activate_horn(HornState(),request(priority_determined=1))


def test_invalid_turn_rejected():
    with pytest.raises(ValueError):
        HornState(turn=0)


def test_invalid_state_rejected():
    with pytest.raises(ValueError):
        HornState(active_turn=1)


def test_courage_consumer_uses_canonical_engine():
    from types import SimpleNamespace
    from courage_test import CourageTestContext,calculate_courage_test_success_probability
    class FakeProfile:
        courage='7+'
    # A production combatant is required; use existing configured model factory through loader.
    from loader import load_all_profiles
    from configured_profile import ConfiguredProfile
    p=next(p for p in load_all_profiles() if p.id=='GUNDABAD_ORC_WARRIOR')
    model=ConfiguredProfile(profile=p)
    expected=calculate_courage_test_success_probability(model,CourageTestContext(roll_modifier=2))
    assert courage_probability_with_horn(model,active_state(),friendly_gundabad=True)==expected
