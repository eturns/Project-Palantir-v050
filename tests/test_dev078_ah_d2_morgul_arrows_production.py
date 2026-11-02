"""DEV-078-AH-D2 — Morgul Arrows production acceptance.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path
from types import SimpleNamespace
import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from morgul_arrows import MorgulArrowsState
from morgul_arrows_service import (
    MorgulArrowsBattlefieldRequest as Request,
    MorgulArrowsShootingWound as Wound,
    build_morgul_arrows_army_evidence,
)
FIXTURE = Path(__file__).parent / 'fixtures/azogs_hunters_all_options.json'

@pytest.fixture(scope="module")
def hunters():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list

def attacker(hunters):
    return next(m.id for m in hunters[0].fielded_models() if m.configured_profile)

def wound(hunters, target="TARGET", **kwargs):
    return Wound(
        turn=1, attacker_model_id=attacker(hunters),
        target_model_id=target, target_is_enemy=kwargs.get("enemy",True),
        attack_is_shooting=kwargs.get("shooting",True),
        wound_not_prevented=kwargs.get("unprevented",True),
    )

def analyse(hunters, request=None):
    a,l=hunters
    kwargs={} if request is None else {"morgul_arrows_request":request}
    return analyse_imported_army(
        a,l,a.total_points(),load_metric_thresholds(),**kwargs
    )

def test_real_rule_registered(hunters):
    assert sum(r.id=="DG_MORGUL_ARROWS" for r in hunters[1].army_rules)==1

def test_initial_shooting_event_tracks_enemy(hunters):
    e=analyse(hunters,Request(shooting_wounds=(wound(hunters),)))["mechanical_morgul_arrows"]
    assert e.state.afflicted == (("TARGET",1),)
    assert e.end_phase is None and e.dashboard_score is None

def test_multiple_shooting_wounds_same_target_one_affliction(hunters):
    w=wound(hunters)
    e=analyse(hunters,Request(shooting_wounds=(w,w)))["mechanical_morgul_arrows"]
    assert e.state.afflicted == (("TARGET",1),)

@pytest.mark.parametrize("change",[
    {"enemy":False}, {"shooting":False}, {"unprevented":False},
])
def test_nonqualifying_event_does_not_afflict(hunters,change):
    e=analyse(hunters,Request(shooting_wounds=(wound(hunters,**change),)))["mechanical_morgul_arrows"]
    assert not e.state.afflicted

def test_same_turn_end_phase_does_not_roll(hunters):
    e=analyse(hunters,Request(shooting_wounds=(wound(hunters),),
                  end_phase_turn=1,dice_by_model_id={}))["mechanical_morgul_arrows"]
    assert e.end_phase.rolled_model_ids == ()

def test_subsequent_end_phase_roll_one_inflicts_wound(hunters):
    first=analyse(hunters,Request(shooting_wounds=(wound(hunters),),
                   end_phase_turn=1,dice_by_model_id={}))["mechanical_morgul_arrows"]
    second=analyse(hunters,Request(initial_state=first.state,
                    end_phase_turn=2,dice_by_model_id={"TARGET":1}))["mechanical_morgul_arrows"]
    assert second.end_phase.rolled_model_ids == ("TARGET",)
    assert second.end_phase.wounded_model_ids == ("TARGET",)

def test_affected_model_persists_on_non_wounding_roll(hunters):
    state=MorgulArrowsState((("TARGET",1),),1)
    e=analyse(hunters,Request(initial_state=state,end_phase_turn=2,
                              dice_by_model_id={"TARGET":6}))["mechanical_morgul_arrows"]
    assert e.state.afflicted == (("TARGET",1),)
    assert e.end_phase.wounded_model_ids == ()

def test_removed_model_no_longer_rolls(hunters):
    state=MorgulArrowsState((("TARGET",1),),1)
    e=analyse(hunters,Request(initial_state=state,removed_model_ids=("TARGET",),
                              end_phase_turn=2,dice_by_model_id={}))["mechanical_morgul_arrows"]
    assert e.state.afflicted == () and e.end_phase.rolled_model_ids == ()

def test_unfielded_shooter_rejected(hunters):
    bad=Wound(1,"UNKNOWN","TARGET",True,True,True)
    with pytest.raises(ValueError,match="not fielded"):
        analyse(hunters,Request(shooting_wounds=(bad,)))

def test_missing_dice_rejected(hunters):
    with pytest.raises(ValueError,match="Explicit dice"):
        analyse(hunters,Request(end_phase_turn=2))

def test_missing_rule_rejected(hunters):
    a,l=hunters
    other=SimpleNamespace(id=l.id,army_rules=[
        r for r in l.army_rules if r.id!="DG_MORGUL_ARROWS"])
    with pytest.raises(ValueError,match="not registered"):
        build_morgul_arrows_army_evidence(a,other,request=Request())

def test_no_context_no_morgul_evidence(hunters):
    assert "mechanical_morgul_arrows" not in analyse(hunters)

def test_existing_scores_unchanged(hunters):
    before=analyse(hunters)
    after=analyse(hunters,Request(shooting_wounds=(wound(hunters),)))
    for k in ("metric_densities","metric_assessments","battlefield_assessments"):
        assert before[k]==after[k]
