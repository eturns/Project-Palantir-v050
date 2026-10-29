"""DEV-077-SMAUG-D2 priority, scope and three-troll regression checks."""
import pytest
from objective_control_override import ObjectiveControlOverride as O, resolve_objective_control_override
from objective_control import resolve_objective_control
from smaug_sheer_dominance import evaluate_smaug_sheer_dominance as evaluate

@pytest.mark.parametrize('first,second,expected', [
    (O.NONE,O.NONE,None), (O.AUTOMATIC_CONTROL,O.NONE,1),
    (O.NONE,O.AUTOMATIC_CONTROL,2),
    (O.AUTOMATIC_CONTROL,O.AUTOMATIC_CONTROL,None),
    (O.SHEER_DOMINANCE,O.AUTOMATIC_CONTROL,1),
    (O.AUTOMATIC_CONTROL,O.SHEER_DOMINANCE,2),
    (O.SHEER_DOMINANCE,O.NONE,1),
    (O.NONE,O.SHEER_DOMINANCE,2),
    (O.SHEER_DOMINANCE,O.SHEER_DOMINANCE,None),
])
def test_override_precedence(first,second,expected):
    assert resolve_objective_control_override(first,second) == expected


def test_smaug_overrides_troll_dominance_even_with_lower_presence():
    assert resolve_objective_control(1,20,O.SHEER_DOMINANCE,O.AUTOMATIC_CONTROL)==1


def test_troll_matching_automatic_effects_still_fall_back_to_presence():
    assert resolve_objective_control(4,2,O.AUTOMATIC_CONTROL,O.AUTOMATIC_CONTROL)==1


def test_rule_and_range_activate():
    r=evaluate(profile_id='SMAUG',rule_ids=frozenset({'SHEER_DOMINANCE'}),
       distance_to_objective_inches=3,objective_range_inches=3)
    assert r.override is O.SHEER_DOMINANCE and r.in_objective_range is True


def test_out_of_range_has_no_override():
    r=evaluate(profile_id='SMAUG',rule_ids=frozenset({'SHEER_DOMINANCE'}),
       distance_to_objective_inches=3.001,objective_range_inches=3)
    assert r.override is O.NONE


def test_unassigned_rule_cannot_activate():
    r=evaluate(profile_id='SMAUG',rule_ids=frozenset(),
       distance_to_objective_inches=1,objective_range_inches=3)
    assert r.override is O.NONE


def test_unknown_objective_range_fails_closed():
    r=evaluate(profile_id='SMAUG',rule_ids=frozenset({'SHEER_DOMINANCE'}),
       distance_to_objective_inches=1,objective_range_inches=None)
    assert r.override is None and r.status=='conditional_not_evaluated'


def test_other_model_rejected():
    with pytest.raises(ValueError,match='requires Smaug'):
        evaluate(profile_id='TT_BILL',rule_ids=frozenset({'SHEER_DOMINANCE'}),
                 distance_to_objective_inches=1,objective_range_inches=3)

@pytest.mark.parametrize('bad', [-1,float('inf'),float('nan'),True])
def test_invalid_distance_rejected(bad):
    with pytest.raises((ValueError,TypeError)):
        evaluate(profile_id='SMAUG',rule_ids=frozenset({'SHEER_DOMINANCE'}),
             distance_to_objective_inches=bad,objective_range_inches=3)
