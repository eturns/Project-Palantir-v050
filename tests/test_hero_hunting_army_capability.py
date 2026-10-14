from dataclasses import replace
from fractions import Fraction as F
import pytest
from hero_resource_state import HeroResourceState
from hero_hunting_resource_adapter import HeroHuntingMethod as M, DeclaredMethodSpend as Spend, reconcile_cross_method_resources
from hero_hunting_evidence_consistency import MethodEvidence, OutcomeType as O, EvidenceStatus as S
from hero_hunting_army_collection import collect_army_hero_hunting_evidence
from hero_hunting_attacker_allocation import AllocatedAttack, validate_army_attack_allocation
from hero_hunting_army_threats import aggregate_army_target_threats
from hero_hunting_unified_defence import UnifiedDefenceEvidence
from hero_hunting_might_will_defence import DefenceResources
from hero_hunting_army_capability import explain_army_hero_hunting_plan


def fixture():
    starts={'a':HeroResourceState(1,0,0),'b':HeroResourceState(0,2,0)}
    records=(
        MethodEvidence('e1','shot','a','leader',M.SHOOTING,O.ELIMINATION,S.VERIFIED,F(1,2),'verified'),
        MethodEvidence('e2','spell','b','leader',M.MAGIC_CAST,O.ELIMINATION,S.VERIFIED,F(1,2),'verified'),
        MethodEvidence('e3','shot_other','a','captain',M.SHOOTING,O.ELIMINATION,S.VERIFIED,F(1,3),'verified'),
        MethodEvidence('e4','control','b','captain',M.MAGIC_CAST,O.CONTROL,S.VERIFIED,F(1,3),'verified'),
    )
    coll=collect_army_hero_hunting_evidence((records,),reconcile_cross_method_resources(starts,()))
    results=(
        UnifiedDefenceEvidence('leader',('shot','spell'),{},F(3,4),F(1,4)),
        UnifiedDefenceEvidence('captain',('shot_other',),{},F(1,3),F(2,3)),
    )
    threats=aggregate_army_target_threats(coll,results)
    return coll,starts,threats


def plan(*picks):
    c,s,t=fixture()
    picks=tuple(AllocatedAttack(eid,slot,Spend(actor,method,**spend)) for eid,slot,actor,method,spend in picks)
    a=validate_army_attack_allocation(c,picks,s)
    return explain_army_hero_hunting_plan(c,a,t)


def test_complete_selected_target_shows_verified_probability():
    r=plan(('e1','one','a',M.SHOOTING,{}),('e2','two','b',M.MAGIC_CAST,{'will':1}))
    assert next(x for x in r.targets if x.target_id=='leader').elimination_probability==F(3,4)


def test_partial_target_plan_must_not_reuse_full_probability():
    r=plan(('e1','one','a',M.SHOOTING,{}))
    lead=next(x for x in r.targets if x.target_id=='leader')
    assert lead.elimination_probability is None
    assert lead.status=='selected_subset_not_evaluated'


def test_other_target_not_allocated_has_no_probability():
    r=plan(('e1','one','a',M.SHOOTING,{}),('e2','two','b',M.MAGIC_CAST,{}))
    captain=next(x for x in r.targets if x.target_id=='captain')
    assert captain.status=='not_allocated' and captain.elimination_probability is None


def test_single_complete_captain_threat():
    r=plan(('e3','three','a',M.SHOOTING,{}))
    captain=next(x for x in r.targets if x.target_id=='captain')
    assert captain.elimination_probability==F(1,3)


def test_control_does_not_become_elimination():
    r=plan(('e4','four','b',M.MAGIC_CAST,{'will':1}))
    captain=next(x for x in r.targets if x.target_id=='captain')
    assert captain.status=='non_elimination_only' and captain.elimination_probability is None


def test_control_and_elimination_on_one_target():
    r=plan(('e3','three','a',M.SHOOTING,{}),('e4','four','b',M.MAGIC_CAST,{}))
    captain=next(x for x in r.targets if x.target_id=='captain')
    assert captain.elimination_probability==F(1,3)
    assert captain.selected_event_ids==('shot_other','control')


def test_remaining_resource_budget_is_reported():
    r=plan(('e1','one','a',M.SHOOTING,{'might':1}),('e2','two','b',M.MAGIC_CAST,{'will':1}))
    assert ('a',0,0,0) in r.remaining_resources
    assert ('b',0,1,0) in r.remaining_resources


def test_no_joint_probability_or_scores():
    r=plan(('e1','one','a',M.SHOOTING,{}),('e2','two','b',M.MAGIC_CAST,{}))
    assert r.any_target_elimination_probability is None
    assert r.dashboard_score is None and r.scenario_score is None


def test_empty_plan_is_unallocated():
    r=plan()
    assert r.selected_attack_count==0
    assert all(t.status=='not_allocated' for t in r.targets)


def test_methods_and_attackers_reported():
    r=plan(('e1','one','a',M.SHOOTING,{}),('e2','two','b',M.MAGIC_CAST,{}))
    lead=next(x for x in r.targets if x.target_id=='leader')
    assert lead.attackers==('a','b') and lead.methods==('magic_cast','shooting')


def test_reject_unmatched_collection_and_threats():
    c,s,t=fixture()
    a=validate_army_attack_allocation(c,(),s)
    with pytest.raises(ValueError,match='Threat targets'):
        explain_army_hero_hunting_plan(c,a,replace(t,targets=t.targets[:1]))


def test_reject_tampered_selected_event_identity():
    c,s,t=fixture()
    a=validate_army_attack_allocation(c,(AllocatedAttack('e1','one',Spend('a',M.SHOOTING)),),s)
    with pytest.raises(ValueError,match='Selection identity'):
        explain_army_hero_hunting_plan(c,replace(a,selected_event_ids=('forged',)),t)


def test_reject_tampered_selection_reference():
    c,s,t=fixture()
    a=validate_army_attack_allocation(c,(),s)
    with pytest.raises(ValueError,match='Selection'):
        explain_army_hero_hunting_plan(c,replace(a,selected_evidence_ids=('forged',)),t)


def test_reject_resource_model_mismatch():
    c,s,t=fixture()
    a=validate_army_attack_allocation(c,(),s)
    mismatch=reconcile_cross_method_resources({'other':HeroResourceState()},())
    with pytest.raises(ValueError,match='resource models'):
        explain_army_hero_hunting_plan(c,replace(a,remaining_resources=mismatch),t)


def test_reject_wrong_collection_type():
    c,s,t=fixture()
    a=validate_army_attack_allocation(c,(),s)
    with pytest.raises(TypeError,match='ArmyHeroHuntingCollection'):
        explain_army_hero_hunting_plan(None,a,t)


def test_reject_wrong_allocation_type():
    c,s,t=fixture()
    with pytest.raises(TypeError,match='ArmyAttackAllocation'):
        explain_army_hero_hunting_plan(c,None,t)
