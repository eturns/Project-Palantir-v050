"""Focused 2024 Gollum 'The Precious' mechanic acceptance."""
from types import SimpleNamespace
import pytest
from gollum_the_precious import (
    ONE_RING_ID, PreciousMovementContext, PreciousCombatContext,
    assess_precious_initial_wargear, assess_precious_charge,
    assess_precious_recovery,
)


def model(id='GT_GOLLUM'):
    return SimpleNamespace(profile=SimpleNamespace(id=id))


def test_starts_with_ring_when_no_enemy_ringbearer():
    e=assess_precious_initial_wargear(model(),enemy_army_has_ringbearer=False)
    assert e.carries_one_ring and e.never_unarmed and e.ring_wargear_id==ONE_RING_ID


def test_does_not_start_with_ring_when_enemy_has_ringbearer():
    assert not assess_precious_initial_wargear(model(),enemy_army_has_ringbearer=True).carries_one_ring


def test_unrelated_model_not_gollum():
    assert assess_precious_initial_wargear(model('GT_GRINNAH'),enemy_army_has_ringbearer=False) is None


def test_initial_reject_unknown_opponent():
    with pytest.raises(TypeError):
        assess_precious_initial_wargear(model(),enemy_army_has_ringbearer=None)


def test_charge_required_if_possible():
    c=PreciousMovementContext(True,True,True)
    e=assess_precious_charge(model(),c)
    assert e.must_charge_enemy_ringbearer and not e.charge_already_resolved


@pytest.mark.parametrize('values',[(True,False,True),(True,True,False),(False,False,True)])
def test_no_forced_charge_when_not_applicable(values):
    assert not assess_precious_charge(model(),PreciousMovementContext(*values)).must_charge_enemy_ringbearer


def test_other_model_no_charge():
    assert not assess_precious_charge(model('GT_KING'),PreciousMovementContext(True,True,True)).must_charge_enemy_ringbearer


def test_absent_ringbearer_but_charge_possible_invalid():
    with pytest.raises(ValueError):
        PreciousMovementContext(False,True,True)


def test_charge_context_is_required():
    with pytest.raises(TypeError):
        assess_precious_charge(model(),None)


def test_recovers_ring_from_enemy_ringbearer_killed_in_combat():
    e=assess_precious_recovery(model(),PreciousCombatContext(True,True))
    assert e.gains_one_ring and e.ring_wargear_id==ONE_RING_ID and not e.state_updated


@pytest.mark.parametrize('values',[(False,True),(True,False),(False,False)])
def test_no_recovery_without_correct_combat_kill(values):
    assert not assess_precious_recovery(model(),PreciousCombatContext(*values)).gains_one_ring


def test_unrelated_model_cannot_recover():
    assert not assess_precious_recovery(model('GT_CAPTAIN'),PreciousCombatContext(True,True)).gains_one_ring


def test_recovery_context_required():
    with pytest.raises(TypeError):
        assess_precious_recovery(model(),None)


def test_invalid_combat_context():
    with pytest.raises(TypeError):
        PreciousCombatContext(True,None)
