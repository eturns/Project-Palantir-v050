"""DEV-077-SMAUG-C4D/E combined combat integration tests."""
from types import SimpleNamespace
from fractions import Fraction
import inspect
import pytest
from army import Army
from profiles import Profile
from smaug_combined_combat_analysis import SmaugCombatRequest, build_smaug_combined_combat_evidence
from smaug_unstoppable_momentum import EngagedDefender
from smaug_colossal_frame import ColossalFrameContext
from services.army_analysis_service import analyse_imported_army

RULES=('IMMOVABLE_OBJECT','UNSTOPPABLE_MOMENTUM','COLOSSAL_FRAME')
def army(rules=RULES, pid='SMAUG'):
    p=Profile(id=pid,name=pid,points=700,movement=12,fight=9,shooting='2+',strength=9,
        defence=9,attacks=4,wounds=20,courage='4+',intelligence='4+',might=3,will=6,fate=0,max_in_army=1)
    for rid in rules:p.special_rules.append(SimpleNamespace(rule=SimpleNamespace(id=rid)))
    a=Army();a.add_profile(p);return a

def test_no_request_is_explicitly_incomplete():
    e=build_smaug_combined_combat_evidence(army())
    assert e.status=='requires_declared_combat_context' and e.immovable_object is None

def test_lost_duel_immovable():
    e=build_smaug_combined_combat_evidence(army(),request=SmaugCombatRequest(lost_duel=True))
    assert e.immovable_object.opponent_must_back_away and not e.immovable_object.smaug_counts_as_trapped
    assert e.unstoppable_momentum is None

def test_won_duel_momentum_replaces_strikes():
    e=build_smaug_combined_combat_evidence(army(),request=SmaugCombatRequest(False,
       (EngagedDefender('a',5),EngagedDefender('b',10)),use_unstoppable_momentum=True))
    assert e.unstoppable_momentum.normal_strikes_allocated==0
    assert e.unstoppable_momentum.expected_wounds==Fraction(1)

def test_cannot_momentum_after_losing():
    with pytest.raises(ValueError,match='won the Duel'):
        build_smaug_combined_combat_evidence(army(),request=SmaugCombatRequest(True,
          (EngagedDefender('a',5),),use_unstoppable_momentum=True))

def test_colossal_frame_preserves_terrain():
    c=ColossalFrameContext('SMAUG',True,True,5,(4,),())
    e=build_smaug_combined_combat_evidence(army(),request=SmaugCombatRequest(False,colossal_frame_context=c))
    assert e.colossal_frame.shooting_into_combat_required_roll is None
    assert e.colossal_frame.terrain_required_rolls==(4,)

def test_missing_rule_never_silently_activates():
    e=build_smaug_combined_combat_evidence(army(rules=()))
    assert e.status=='missing_combat_rule_assignments'
    with pytest.raises(ValueError,match='Missing Smaug combat rules'):
        build_smaug_combined_combat_evidence(army(rules=()),request=SmaugCombatRequest(False))

def test_non_smaug_isolation():
    assert build_smaug_combined_combat_evidence(army(pid='TT_BILL')) is None
    with pytest.raises(ValueError,match='requires Smaug'):
        build_smaug_combined_combat_evidence(army(pid='TT_BILL'),request=SmaugCombatRequest(False))

def test_service_contract_and_scoring_isolation():
    source=inspect.getsource(analyse_imported_army)
    assert 'smaug_combat_request' in inspect.signature(analyse_imported_army).parameters
    assert 'build_smaug_combined_combat_evidence(' in source
    assert "result['mechanical_smaug_combat']" in source
    assert 'offence_value=offence_score, shooting_value=shooting_score' in source
    assert build_smaug_combined_combat_evidence(army(),request=SmaugCombatRequest(False)).dashboard_score is None

def test_registration_composite_keys():
    import csv
    with open('data/profiles/profile_special_rules.csv',newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    assert all(sum(x['profile_id']=='SMAUG' and x['rule_id']==r for x in rows)==1 for r in RULES)
