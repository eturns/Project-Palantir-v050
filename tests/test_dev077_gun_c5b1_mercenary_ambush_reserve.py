from types import SimpleNamespace
import pytest

from mercenary_ambush_reserve import (
    AmbushReserve, ArrivalDecisionOwner,
    eligible_for_mercenary_ambush, eligible_warbands_from_definition,
    intelligence_test_passed, resolve_ambush_arrival_decision,
)
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules


def test_eligibility_requires_captain_and_only_goblin_mercenaries():
    assert eligible_for_mercenary_ambush('GOBLIN_MERCENARY_CAPTAIN', ['GOBLIN_MERCENARY'] * 4)
    assert eligible_for_mercenary_ambush('GOBLIN_MERCENARY_CAPTAIN', [])
    assert not eligible_for_mercenary_ambush('AZOG_THE_DEFILER', ['GOBLIN_MERCENARY'])
    assert not eligible_for_mercenary_ambush('GOBLIN_MERCENARY_CAPTAIN', ['GUNDABAD_ORC_WARRIOR'])


def test_definition_warband_isolation_and_missing_leader():
    def entry(wb, pid, leader=False):
        return SimpleNamespace(warband_id=wb, profile_id=pid, is_warband_leader=leader)
    definition = SimpleNamespace(entries=[
        entry('eligible', 'GOBLIN_MERCENARY_CAPTAIN', True),
        entry('eligible', 'GOBLIN_MERCENARY'),
        entry('ineligible', 'GOBLIN_MERCENARY_CAPTAIN', True),
        entry('ineligible', 'GUNDABAD_OGRE'),
        entry('leaderless', 'GOBLIN_MERCENARY'),
    ])
    assert eligible_warbands_from_definition(definition) == ('eligible',)


def test_ambush_registration_for_both_goblin_profiles():
    profiles = {p.id: p for p in load_all_profiles()}
    load_profile_special_rules(profiles, load_special_rules())
    for pid in ('GOBLIN_MERCENARY_CAPTAIN', 'GOBLIN_MERCENARY'):
        assert 'MERCENARY_AMBUSH' in {a.rule.id for a in profiles[pid].special_rules}
    assert 'MERCENARY_AMBUSH' not in {a.rule.id for a in profiles['GUNDABAD_OGRE'].special_rules}


def test_intelligence_target_six_plus_uses_2d6():
    assert not intelligence_test_passed('6+', (2, 3))
    assert intelligence_test_passed('6+', (3, 3))
    assert intelligence_test_passed('6+', (6, 6))


def test_arrival_rights_depend_on_intelligence_outcome():
    reserve = AmbushReserve('warband_1')
    common = dict(reserve=reserve, turn=2, end_of_controlling_activation=True, intelligence_target='6+')
    assert resolve_ambush_arrival_decision(**common, dice=(3, 3)) is ArrivalDecisionOwner.CONTROLLING_PLAYER
    assert resolve_ambush_arrival_decision(**common, dice=(2, 3)) is ArrivalDecisionOwner.OPPOSING_PLAYER


def test_no_test_before_turn_two_or_wrong_phase_or_after_arrival():
    reserve = AmbushReserve('warband_1')
    kwargs = dict(reserve=reserve, intelligence_target='6+', dice=(3, 3))
    assert resolve_ambush_arrival_decision(**kwargs, turn=1, end_of_controlling_activation=True) is None
    assert resolve_ambush_arrival_decision(**kwargs, turn=2, end_of_controlling_activation=False) is None
    arrived = AmbushReserve('warband_1', in_reserve=False, arrived=True)
    assert resolve_ambush_arrival_decision(arrived, turn=3, end_of_controlling_activation=True, intelligence_target='6+', dice=(3, 3)) is None


def test_rejects_bad_dice_or_invalid_state():
    for dice in ((0, 6), (7, 1), (True, 2), (1,), [1, 6]):
        with pytest.raises(ValueError):
            intelligence_test_passed('6+', dice)
    with pytest.raises(ValueError):
        AmbushReserve('bad', in_reserve=True, arrived=True)
    with pytest.raises(ValueError):
        resolve_ambush_arrival_decision(AmbushReserve('a'), turn=0, end_of_controlling_activation=True, intelligence_target='6+', dice=(3, 3))
