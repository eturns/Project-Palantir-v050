from fractions import Fraction as F
from dataclasses import replace
import pytest
from hero_resource_state import HeroResourceState
from hero_hunting_resource_adapter import HeroHuntingMethod, reconcile_cross_method_resources
from hero_hunting_evidence_consistency import MethodEvidence, EvidenceStatus, OutcomeType
from hero_hunting_army_collection import collect_army_hero_hunting_evidence
from hero_hunting_unified_defence import UnifiedDefenceEvidence
from hero_hunting_might_will_defence import DefenceResources
from hero_hunting_army_threats import aggregate_army_target_threats as aggregate


def observation(eid, target='hero', outcome=OutcomeType.ELIMINATION, status=EvidenceStatus.VERIFIED):
    return MethodEvidence(eid,eid,'attacker',target,HeroHuntingMethod.MELEE,outcome,status,
                          F(1,2) if status is EvidenceStatus.VERIFIED else None,
                          'verified' if status is EvidenceStatus.VERIFIED else None)


def collection(*obs):
    resources=reconcile_cross_method_resources({'attacker':HeroResourceState(),
                   'hero':HeroResourceState(),'other':HeroResourceState()},())
    return collect_army_hero_hunting_evidence((tuple(obs),),resources)


def result(target='hero', ids=('a',), p=F(1,2)):
    return UnifiedDefenceEvidence(target,ids,{DefenceResources(1,0,0,0):1-p,
        DefenceResources(0,0,0,0):p},p,1-p)


def test_empty_collection():
    r=aggregate(collection(),())
    assert r.targets==() and r.any_target_elimination_probability is None


def test_one_target_verified_probability():
    r=aggregate(collection(observation('a')),(result(),))
    assert r.targets[0].elimination_probability==F(1,2)


def test_two_targets_not_combined():
    r=aggregate(collection(observation('a'),observation('b','other')),
                (result(),result('other',('b',),F(1,4))))
    assert [x.elimination_probability for x in r.targets]==[F(1,2),F(1,4)]
    assert r.any_target_elimination_probability is None


def test_missing_result_is_unresolved_not_zero():
    r=aggregate(collection(observation('a')),())
    assert r.targets[0].elimination_probability is None


def test_no_elimination_events_can_be_zero_with_explicit_result():
    r=aggregate(collection(observation('ctrl',outcome=OutcomeType.CONTROL)),
                (result(ids=(),p=F(0)),))
    assert r.targets[0].elimination_probability==0


def test_control_event_not_used_as_elimination():
    with pytest.raises(ValueError,match='match verified'):
        aggregate(collection(observation('ctrl',outcome=OutcomeType.CONTROL)),(result(ids=('ctrl',)),))


def test_unresolved_event_does_not_become_verified_probability():
    c=collection(observation('a'),observation('b',status=EvidenceStatus.UNRESOLVED))
    r=aggregate(c,(result(),))
    assert r.targets[0].status=='partial_unresolved'


def test_duplicate_result_rejected():
    with pytest.raises(ValueError,match='Duplicate target'):
        aggregate(collection(observation('a')),(result(),result()))


def test_unknown_result_target_rejected():
    with pytest.raises(ValueError,match='unknown target'):
        aggregate(collection(observation('a')),(result('stranger'),))


def test_missing_verified_event_rejected():
    with pytest.raises(ValueError,match='match verified'):
        aggregate(collection(observation('a')),(result(ids=()),))


def test_extra_event_rejected():
    with pytest.raises(ValueError,match='match verified'):
        aggregate(collection(observation('a')),(result(ids=('a','b')),))


def test_invalid_survival_complement_rejected():
    bad=replace(result(),survival_probability=F(1,4))
    with pytest.raises(ValueError,match='inconsistent'):
        aggregate(collection(observation('a')),(bad,))


def test_scores_remain_unmodified():
    r=aggregate(collection(observation('a')),(result(),))
    assert r.dashboard_score is None and r.scenario_score is None
