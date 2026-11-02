"""DEV-078-AoG-D2: real-army Horn acceptance. Author: Edward Turns (Project Lead)."""
from dataclasses import replace
from types import SimpleNamespace
import pytest
from loader import load_all_profiles
from configured_profile import ConfiguredProfile
from gundabad_horn_of_gorgoroth import HornState, advance_turn
from gundabad_horn_of_gorgoroth_service import (
    HornArmyRequest, HornCourageTarget, build_horn_of_gorgoroth_army_evidence
)
from tests.test_dev077_gun_d2b_runtime_import_integrity import imported as imported_fixture
from army_loader import load_army_rules, load_army_lists, load_factions
from analysis_loader import load_metric_thresholds
from services.army_analysis_service import analyse_imported_army


@pytest.fixture(scope='module')
def setup(imported_fixture):
    definition,army,army_list=imported_fixture
    lists=load_army_lists(load_factions())
    load_army_rules(lists)
    army_list.army_rules=lists['GUNDABAD'].army_rules
    return definition,army,army_list


def request(setup,**kw):
    _,army,_=setup
    friend=next(m for m in army.fielded_models() if m.configured_profile is not None)
    profiles={p.id:p for p in load_all_profiles()}
    enemy=HornCourageTarget('enemy-1',ConfiguredProfile(profiles['IH_WR']))
    base=dict(state=HornState(),general_alive=True,general_on_battlefield=True,
              priority_determined=True,activate=True,
              friendly_model_ids=(friend.id,),enemies=(enemy,))
    base.update(kw)
    return HornArmyRequest(**base)


def evidence(setup,req=None):
    d,a,l=setup
    return build_horn_of_gorgoroth_army_evidence(a,l,army_definition=d,
                                                  request=req or request(setup))


def test_rule_registered(setup):
    assert any(x.id=='GUNDABAD_HORN_OF_GORGOROTH' for x in setup[2].army_rules)


def test_general_resolved(setup):
    assert evidence(setup).general_model_id in {m.id for m in setup[1].fielded_models()}


def test_activation(setup):
    assert evidence(setup).activation.activated


def test_courage_results_present(setup):
    assert {x.relationship for x in evidence(setup).courage}=={'friendly_gundabad','enemy'}


def test_friendly_probability_increases(setup):
    r=next(x for x in evidence(setup).courage if x.relationship=='friendly_gundabad')
    assert r.modified_probability>=r.ordinary_probability


def test_enemy_probability_decreases(setup):
    r=next(x for x in evidence(setup).courage if x.relationship=='enemy')
    assert r.modified_probability<=r.ordinary_probability


def test_declaration_not_made(setup):
    e=evidence(setup,request(setup,activate=False))
    assert e.activation.status=='not_declared'
    assert all(x.modified_probability==x.ordinary_probability for x in e.courage)


@pytest.mark.parametrize('field', ['general_alive','general_on_battlefield','priority_determined'])
def test_ineligible_general_or_timing(setup,field):
    e=evidence(setup,request(setup,**{field:False}))
    assert not e.activation.activated


def test_once_per_game_state_persists(setup):
    first=evidence(setup)
    later=evidence(setup,request(setup,state=advance_turn(first.activation.state)))
    assert later.activation.status=='already_used'
    assert all(x.modified_probability==x.ordinary_probability for x in later.courage)


def test_unknown_friendly_rejected(setup):
    with pytest.raises(ValueError,match='Friendly target'):
        evidence(setup,request(setup,friendly_model_ids=('not-fielded',)))


def test_wrong_army_rejected(setup):
    d,a,l=setup
    with pytest.raises(ValueError,match='Army of Gundabad'):
        build_horn_of_gorgoroth_army_evidence(a,SimpleNamespace(id='DG_PITS',army_rules=l.army_rules),
                                               army_definition=d,request=request(setup))


def test_missing_general_rejected(setup):
    d,a,l=setup
    bad=replace(d,leader_profile_id='NOT_A_MODEL')
    with pytest.raises(ValueError,match='General'):
        build_horn_of_gorgoroth_army_evidence(a,l,army_definition=bad,request=request(setup))


def test_service_exposes_diagnostic(setup):
    d,a,l=setup
    result=analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds(),
                                 gundabad_army_definition=d,gundabad_horn_request=request(setup))
    assert result['mechanical_horn_of_gorgoroth'].activation.activated
    assert result['mechanical_horn_of_gorgoroth'].dashboard_score is None


def test_scores_preserved(setup):
    d,a,l=setup
    baseline=analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds())
    active=analyse_imported_army(a,l,max(a.total_points(),2000),load_metric_thresholds(),
                                gundabad_army_definition=d,gundabad_horn_request=request(setup))
    for key in ('metric_densities','metric_assessments','battlefield_assessments'):
        assert baseline[key]==active[key]
