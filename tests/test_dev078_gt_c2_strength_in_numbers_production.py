"""DEV-078-GT-C2 real-army Strength in Numbers acceptance.
Author: Edward Turns (Project Lead).
"""
from dataclasses import replace
from fractions import Fraction
from types import SimpleNamespace
import pytest
from tests.test_dev077_gt_d1_import_integrity import production as gt_production
from army_loader import load_army_rules
from goblin_town_strength_in_numbers_service import (
    StrengthInNumbersArmyRequest, build_strength_in_numbers_army_evidence,
)
from courage_test import CourageTestContext
from analysis_loader import load_metric_thresholds
from services.army_analysis_service import analyse_imported_army


@pytest.fixture(scope="module")
def production(gt_production):
    _, lists, imported = gt_production
    load_army_rules(lists)
    definition, army, army_list = imported
    army_list.army_rules = lists["GOBLIN_TOWN"].army_rules
    return definition, army, army_list


def request(production, **changes):
    _, army, _ = production
    ids = tuple((m.id, True) for m in army.fielded_models()
                if m.configured_profile is not None)
    kwargs=dict(army_broken=False, terror_charge_tests_by_model_id=ids)
    kwargs.update(changes)
    return StrengthInNumbersArmyRequest(**kwargs)


def assess(production, req=None):
    _, army, army_list = production
    return build_strength_in_numbers_army_evidence(
        army,army_list,request=req if req is not None else request(production))


def test_registered_rule(production):
    assert "GT_STRENGTH_IN_NUMBERS" in {r.id for r in production[2].army_rules}


def test_real_goblins_receive_bonus(production):
    evidence=assess(production)
    goblins=[m for m in evidence.model_tests if m.profile_id=="GT_WARRIOR"]
    assert goblins and all(m.result.bonus==1 for m in goblins)


def test_king_receives_bonus(production):
    kings=[m for m in assess(production).model_tests if m.profile_id=="GT_KING"]
    assert len(kings)==1 and kings[0].result.entitled


def test_gollum_not_goblin(production):
    non_goblins=[m for m in assess(production).model_tests if m.profile_id=="GT_GOLLUM"]
    assert all(not m.result.entitled for m in non_goblins)


def test_broken_army_no_bonus(production):
    assert all(m.result.bonus==0 for m in
               assess(production,request(production,army_broken=True)).model_tests)


def test_not_terror_charge_no_bonus(production):
    req=request(production)
    req=replace(req,terror_charge_tests_by_model_id=tuple((mid,False)
                for mid,_ in req.terror_charge_tests_by_model_id))
    assert all(m.result.bonus==0 for m in assess(production,req).model_tests)


def test_ordinary_and_modified_probabilities(production):
    ev=assess(production)
    assert all(m.result.modified_probability>=m.result.ordinary_probability
               for m in ev.model_tests)


def test_existing_modifier_stacks(production):
    ev=assess(production,request(production,
        base_courage_context=CourageTestContext(roll_modifier=-2)))
    for m in ev.model_tests:
        if m.result.entitled:
            assert m.result.base_modifier==-2 and m.result.modified_modifier==-1


def test_unknown_fielded_model_rejected(production):
    with pytest.raises(ValueError,match="not fielded"):
        assess(production,request(production,
            terror_charge_tests_by_model_id=(("not-a-model",True),)))


def test_duplicate_model_rejected(production):
    mid=request(production).terror_charge_tests_by_model_id[0][0]
    with pytest.raises(ValueError,match="Duplicate"):
        assess(production,request(production,
            terror_charge_tests_by_model_id=((mid,True),(mid,False))))


def test_non_boolean_terror_rejected(production):
    mid=request(production).terror_charge_tests_by_model_id[0][0]
    with pytest.raises(TypeError,match="bool"):
        assess(production,request(production,
            terror_charge_tests_by_model_id=((mid,1),)))


def test_wrong_army_rejected(production):
    _,army,alist=production
    with pytest.raises(ValueError,match="Goblin-town"):
        build_strength_in_numbers_army_evidence(
            army,SimpleNamespace(id="GUNDABAD",army_rules=alist.army_rules),
            request=request(production))


def test_unregistered_rule_rejected(production):
    _,army,alist=production
    with pytest.raises(ValueError,match="not registered"):
        build_strength_in_numbers_army_evidence(
            army,SimpleNamespace(id=alist.id,army_rules=[]),
            request=request(production))


def test_empty_test_requests_valid(production):
    ev=assess(production,request(production,terror_charge_tests_by_model_id=()))
    assert ev.model_tests == ()


def test_diagnostic_only(production):
    ev=assess(production)
    assert ev.dashboard_score is None and ev.scenario_score is None


def test_analysis_service_exposes_diagnostic(production):
    _,army,alist=production
    result=analyse_imported_army(army,alist,max(army.total_points(),2000),
        load_metric_thresholds(),goblin_town_strength_request=request(production))
    assert result["mechanical_strength_in_numbers"].model_tests


def test_no_request_does_not_add_diagnostic(production):
    _,army,alist=production
    result=analyse_imported_army(army,alist,max(army.total_points(),2000),
        load_metric_thresholds())
    assert "mechanical_strength_in_numbers" not in result


def test_scores_preserved(production):
    _,army,alist=production
    limit=max(army.total_points(),2000)
    thresholds=load_metric_thresholds()
    base=analyse_imported_army(army,alist,limit,thresholds)
    modified=analyse_imported_army(army,alist,limit,thresholds,
        goblin_town_strength_request=request(production))
    for key in ("metric_densities","metric_assessments","battlefield_assessments"):
        assert base[key]==modified[key]
