"""A3-2D weapon qualification tests, injected resolver for deterministic scope."""
from types import SimpleNamespace as NS
import pytest
from offence_weapon_qualification import qualify_weapon_options, build_weapon_qualified_offence_report


def cfg(*ids):
    return NS(profile=NS(id='P'), effective_wargear=tuple(NS(id=i) for i in ids))


def result(p=0.5, weighted=None):
    return NS(uncharged=p, charged_without_cavalry_bonus=p,
              charged_with_cavalry_bonus=p, weighted=weighted)


def evaluate(config, *, outcome=None):
    calls=[]
    def calc(model, weapon_id):
        calls.append(weapon_id)
        return (outcome or result())
    return qualify_weapon_options(config, evaluator=calc), calls


def test_single_known_weapon_is_recognised_without_automatic_choice():
    row, calls = evaluate(cfg('WG_HAND_WEAPON','WG_ARMOUR'))
    assert row['status']=='single_recognised_option'
    assert row['candidate_weapon_ids']==['WG_HAND_WEAPON']
    assert row['selected_weapon_id'] is None and not row['automatic_choice_made']
    assert calls==['WG_HAND_WEAPON']


def test_multiple_weapons_not_auto_optimised():
    row,calls=evaluate(cfg('WG_TWO_HANDED_WEAPON','WG_HAND_WEAPON'))
    assert row['status']=='multiple_options'
    assert calls==['WG_HAND_WEAPON','WG_TWO_HANDED_WEAPON']
    assert row['selected_weapon_id'] is None


def test_unknown_custom_wargear_fails_closed_and_is_not_evaluated():
    row,calls=evaluate(cfg('WG_HAND_WEAPON','CUSTOM_UNAUDITED'))
    assert row['status']=='unresolved'
    assert row['unclassified_wargear_ids']==['CUSTOM_UNAUDITED']
    assert calls==[]


def test_no_recognised_melee_weapon_not_assumed_unarmed():
    row,calls=evaluate(cfg('WG_SHIELD','WG_ARMOUR'))
    assert row['status']=='unresolved' and calls==[]


def test_shield_and_bow_do_not_become_additional_melee_choices():
    row,_=evaluate(cfg('WG_HAND_WEAPON','WG_SHIELD','WG_ELF_BOW'))
    assert row['candidate_weapon_ids']==['WG_HAND_WEAPON']


def test_special_named_weapon_not_guessed_from_name():
    row,_=evaluate(cfg('WG_SPECIAL_SWORD'))
    assert row['unclassified_wargear_ids']==['WG_SPECIAL_SWORD']


def test_duplicate_equipment_ids_rejected():
    with pytest.raises(ValueError,match='Duplicate'):
        evaluate(cfg('WG_HAND_WEAPON','WG_HAND_WEAPON'))


@pytest.mark.parametrize('invalid',[-0.1,1.1,float('nan'),float('inf'),None])
def test_unqualified_probability_rejected(invalid):
    with pytest.raises(ValueError,match='probability'):
        evaluate(cfg('WG_HAND_WEAPON'),outcome=result(invalid))


def test_weighted_probability_rejected():
    with pytest.raises(ValueError,match='charge probability'):
        evaluate(cfg('WG_HAND_WEAPON'),outcome=result(weighted=0.5))


def army():
    a=NS(profile=NS(id='P'),effective_wargear=(NS(id='WG_HAND_WEAPON'),))
    b=NS(profile=NS(id='Q'),effective_wargear=(NS(id='WG_SHIELD'),))
    return NS(entries=(NS(counts_as_model=True,configured_profile=a,quantity=2),
                       NS(counts_as_model=True,configured_profile=b,quantity=1)))


def baseline():
    base={
        'stage':'DEV-082-A3-2C','candidate_raw_density':None,'comparable':False,
        'profile_rows':[], 'qualified_unresolved_model_counts': {'trapping':3},
        'dashboard_score':None,'scenario_score':None,
    }
    for pid,n in [('P',2),('Q',1)]:
        base['profile_rows'].append({'profile_id':pid,'quantity':n,
           'uncharged_probability':0.5,
           'qualification':{'trapping':{'status':'unresolved','reason':'trapping'},
              'weapon_selection':{'status':'unresolved','reason':'unverified'}}})
    return base


def test_report_preserves_unmodified_probabilities_and_source():
    original=baseline()
    report=build_weapon_qualified_offence_report(army(),report_builder=lambda a:original,evaluator=lambda a,w:result())
    assert report['stage']=='DEV-082-A3-2D'
    assert report['profile_rows'][0]['uncharged_probability']==0.5
    assert original['profile_rows'][0]['qualification']['weapon_selection']['reason']=='unverified'
    assert report['weapon_model_status_counts']=={'single_recognised_option':2,'unresolved':1}


def test_report_recounts_only_genuinely_unresolved_conditions():
    report=build_weapon_qualified_offence_report(army(),report_builder=lambda a:baseline(),evaluator=lambda a,w:result())
    assert report['qualified_unresolved_model_counts']=={
        'trapping':3,'no_recognised_melee_weapon_cannot_assume_unarmed':1}
    assert report['candidate_raw_density'] is None
    assert report['dashboard_score'] is None


def test_wrong_source_stage_rejected():
    x=baseline();x['stage']='wrong'
    with pytest.raises(ValueError, match='A3-2C'):
        build_weapon_qualified_offence_report(army(),report_builder=lambda a:x,evaluator=lambda a,w:result())


def test_source_claiming_candidate_rejected():
    x=baseline();x['candidate_raw_density']=0.5
    with pytest.raises(ValueError, match='unavailable'):
        build_weapon_qualified_offence_report(army(),report_builder=lambda a:x,evaluator=lambda a,w:result())


def test_row_identity_mismatch_rejected():
    x=baseline();x['profile_rows'][0]['profile_id']='WRONG'
    with pytest.raises(ValueError, match='identity'):
        build_weapon_qualified_offence_report(army(),report_builder=lambda a:x,evaluator=lambda a,w:result())


def test_report_does_not_change_army():
    a=army();before=tuple((e.quantity,e.configured_profile.profile.id) for e in a.entries)
    build_weapon_qualified_offence_report(a,report_builder=lambda x:baseline(),evaluator=lambda a,w:result())
    assert before==tuple((e.quantity,e.configured_profile.profile.id) for e in a.entries)
