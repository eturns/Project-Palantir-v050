"""DEV-078-GT-D3: real-army prisoner integration acceptance.

Author: Edward Turns (Project Lead).
Fixtures resolve both friendly and opposing armies to real fielded models.
"""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from tests.test_dev077_gt_d1_import_integrity import production as gt_production
from army import Army
from army_loader import load_army_rules
from configured_profile import ConfiguredProfile
from profile_classification import ModelType
from analysis_loader import load_metric_thresholds
from services.army_analysis_service import analyse_imported_army
from goblin_town_prisoner_state import PrisonerChoice, PrisonerState, RULE_ID
from goblin_town_prisoner_victory_points import CaptorEndgameStatus
from goblin_town_prisoner_service import (
    PrisonerCombatEvent, PrisonerArmyRequest,
    build_goblin_town_prisoner_army_evidence,
)


@pytest.fixture(scope="module")
def production(gt_production):
    profiles, lists, (definition, friendly, army_list) = gt_production
    load_army_rules(lists)
    army_list.army_rules = lists["GOBLIN_TOWN"].army_rules
    enemy = Army()
    for pid in ("IH_DAIN", "BOFUR_CHAMPION_OF_EREBOR", "IH_WR"):
        enemy.add_configured_profile(ConfiguredProfile(profiles[pid]))
    friends = friendly.fielded_models()
    enemies = enemy.fielded_models()
    king = next(m for m in friends if m.profile_id == "GT_KING")
    grinnah = next(m for m in friends if m.profile_id == "GT_GRINNAH")
    dain = next(m for m in enemies if m.profile_id == "IH_DAIN")
    bofur = next(m for m in enemies if m.profile_id == "BOFUR_CHAMPION_OF_EREBOR")
    warrior = next(m for m in enemies if m.profile_id == "IH_WR")
    return (definition, friendly, army_list, enemy, king, grinnah, dain, bofur, warrior, profiles)


def request(production, *, events=None, vp=None, survival=None, **kwargs):
    _,_,_,enemy,king,grinnah,dain,bofur,_,_=production
    if events is None:
        events=(PrisonerCombatEvent(king.id,dain.id,True,PrisonerChoice.TAKE_NEW),)
    if survival is None and vp is not None:
        survival=(
            CaptorEndgameStatus(king.id,"GT_KING",True),
            CaptorEndgameStatus(grinnah.id,"GT_GRINNAH",True),
        )
    return PrisonerArmyRequest(
        enemy_army=enemy,
        events=events,
        scenario_victory_points=vp,
        captors_at_end=() if survival is None else survival,
        **kwargs,
    )


def evidence(production, req=None):
    _,army,army_list,*_=production
    return build_goblin_town_prisoner_army_evidence(
        army,army_list,request=request(production) if req is None else req,
    )


def test_rule_registered(production):
    assert RULE_ID in {r.id for r in production[2].army_rules}


def test_king_captures_real_enemy_hero(production):
    ev=evidence(production)
    assert ev.event_outcomes[0].captured
    assert ev.final_state.prisoners[0].captor_model_id==production[4].id
    assert ev.final_state.prisoners[0].victim_model_id==production[6].id


def test_capturing_does_not_create_vp_without_endgame(production):
    ev=evidence(production)
    assert ev.endgame is None and ev.dashboard_score is None


def test_real_grinnah_capture(production):
    event=PrisonerCombatEvent(production[5].id,production[7].id,True,PrisonerChoice.TAKE_NEW)
    ev=evidence(production,request(production,events=(event,)))
    assert ev.event_outcomes[0].captured


def test_two_independent_captor_slots(production):
    king,grinnah,dain,bofur=production[4:8]
    events=(
        PrisonerCombatEvent(king.id,dain.id,True,PrisonerChoice.TAKE_NEW),
        PrisonerCombatEvent(grinnah.id,bofur.id,True,PrisonerChoice.TAKE_NEW),
    )
    ev=evidence(production,request(production,events=events,vp=17))
    assert len(ev.final_state.prisoners)==2
    assert ev.endgame.awarded_prisoner_victory_points==2
    assert ev.endgame.final_victory_points==19


def test_twenty_vp_ceiling_with_two_captors(production):
    king,grinnah,dain,bofur=production[4:8]
    events=(
        PrisonerCombatEvent(king.id,dain.id,True,PrisonerChoice.TAKE_NEW),
        PrisonerCombatEvent(grinnah.id,bofur.id,True,PrisonerChoice.TAKE_NEW),
    )
    ev=evidence(production,request(production,events=events,vp=19))
    assert ev.endgame.awarded_prisoner_victory_points==1
    assert ev.endgame.final_victory_points==20


def test_dead_king_cannot_score(production):
    king,grinnah=production[4:6]
    survival=(
        CaptorEndgameStatus(king.id,"GT_KING",False),
        CaptorEndgameStatus(grinnah.id,"GT_GRINNAH",True),
    )
    ev=evidence(production,request(production,vp=6,survival=survival))
    assert ev.endgame.awarded_prisoner_victory_points==0


def test_non_hero_enemy_is_casualty_not_prisoner(production):
    king,warrior=production[4],production[8]
    ev=evidence(production,request(production,events=(
        PrisonerCombatEvent(king.id,warrior.id,True,PrisonerChoice.TAKE_NEW),)))
    assert ev.final_state.prisoners == ()
    assert ev.final_state.casualty_ids==(warrior.id,)


def test_non_combat_death_is_not_a_capture(production):
    king,dain=production[4],production[6]
    ev=evidence(production,request(production,events=(
        PrisonerCombatEvent(king.id,dain.id,False,PrisonerChoice.TAKE_NEW),)))
    assert ev.final_state==PrisonerState()


def test_captor_cannot_be_random_friendly_goblin(production):
    warrior=next(m for m in production[1].fielded_models() if m.profile_id=="GT_WARRIOR")
    with pytest.raises(ValueError,match="Goblin King or Grinnah"):
        evidence(production,request(production,events=(
            PrisonerCombatEvent(warrior.id,production[6].id,True,PrisonerChoice.TAKE_NEW),)))


def test_enemy_cannot_act_as_captor(production):
    with pytest.raises(ValueError,match="friendly fielded"):
        evidence(production,request(production,events=(
            PrisonerCombatEvent(production[6].id,production[7].id,True,PrisonerChoice.TAKE_NEW),)))


def test_unknown_victim_rejected(production):
    with pytest.raises(ValueError,match="enemy fielded"):
        evidence(production,request(production,events=(
            PrisonerCombatEvent(production[4].id,"unknown-enemy",True,PrisonerChoice.TAKE_NEW),)))


def test_victim_in_friendly_army_rejected(production):
    with pytest.raises(ValueError,match="enemy fielded"):
        evidence(production,request(production,events=(
            PrisonerCombatEvent(production[4].id,production[5].id,True,PrisonerChoice.TAKE_NEW),)))


def test_same_victim_cannot_die_twice(production):
    king,dain=production[4],production[6]
    ev=PrisonerCombatEvent(king.id,dain.id,True,PrisonerChoice.TAKE_NEW)
    with pytest.raises(ValueError,match="already"):
        evidence(production,request(production,events=(ev,ev)))


def test_replace_existing_prisoner_keeps_casualty_history(production):
    king,dain,bofur=production[4],production[6],production[7]
    ev=evidence(production,request(production,events=(
        PrisonerCombatEvent(king.id,dain.id,True,PrisonerChoice.TAKE_NEW),
        PrisonerCombatEvent(king.id,bofur.id,True,PrisonerChoice.TAKE_NEW),
    ),vp=12))
    assert ev.event_outcomes[1].status=="replaced"
    assert len(ev.final_state.casualty_ids)==2
    assert len(ev.final_state.prisoners)==1
    assert ev.endgame.awarded_prisoner_victory_points==1


def test_wrong_army_rejected(production):
    _,army,army_list,*_=production
    with pytest.raises(ValueError,match="Goblin-town"):
        build_goblin_town_prisoner_army_evidence(
            army,SimpleNamespace(id="GUNDABAD",army_rules=army_list.army_rules),
            request=request(production))


def test_missing_registered_rule_rejected(production):
    _,army,army_list,*_=production
    with pytest.raises(ValueError,match="not registered"):
        build_goblin_town_prisoner_army_evidence(
            army,SimpleNamespace(id="GOBLIN_TOWN",army_rules=[]),
            request=request(production))


def test_survival_profile_must_match_real_friendly_captor(production):
    king=production[4]
    statuses=(CaptorEndgameStatus(king.id,"GT_GRINNAH",True),)
    with pytest.raises(ValueError,match="contradicts"):
        evidence(production,request(production,vp=5,survival=statuses))


def test_missing_survival_not_silently_assumed(production):
    with pytest.raises(ValueError,match="Missing captor"):
        evidence(production,request(production,vp=5,survival=()))


def test_duplicate_victim_army_ids_rejected(production):
    # Reusing the friendly roster as the opposing one introduces duplicate IDs.
    with pytest.raises(ValueError,match="must be distinct"):
        evidence(production,replace(request(production),enemy_army=production[1]))


def test_reject_nonbool_kill(production):
    king,dain=production[4],production[6]
    with pytest.raises(TypeError,match="boolean"):
        evidence(production,request(production,events=(
            PrisonerCombatEvent(king.id,dain.id,1,PrisonerChoice.TAKE_NEW),)))


def test_no_events_no_endgame_is_diagnostic_only(production):
    ev=evidence(production,request(production,events=()))
    assert ev.final_state==PrisonerState()
    assert ev.endgame is None


def test_service_exposes_diagnostic(production):
    _,army,army_list,*_=production
    result=analyse_imported_army(army,army_list,max(army.total_points(),2000),
        load_metric_thresholds(),goblin_town_prisoner_request=request(production))
    assert result["mechanical_goblin_town_prisoners"].event_outcomes[0].captured


def test_no_request_no_prisoner_diagnostic(production):
    _,army,army_list,*_=production
    result=analyse_imported_army(army,army_list,max(army.total_points(),2000),
        load_metric_thresholds())
    assert "mechanical_goblin_town_prisoners" not in result


def test_existing_scores_preserved(production):
    _,army,army_list,*_=production
    args=(army,army_list,max(army.total_points(),2000),load_metric_thresholds())
    original=analyse_imported_army(*args)
    with_prisoner=analyse_imported_army(*args,
        goblin_town_prisoner_request=request(production,vp=19))
    for key in ("metric_densities","metric_assessments","battlefield_assessments"):
        assert original[key]==with_prisoner[key]
    assert with_prisoner["mechanical_goblin_town_prisoners"].scenario_score is None
