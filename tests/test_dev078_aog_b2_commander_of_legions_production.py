"""DEV-078-AoG-B2: production Commander of Legions acceptance.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path
from dataclasses import replace
from types import SimpleNamespace
import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from tests.test_dev077_gun_d2b_runtime_import_integrity import imported as imported_fixture
from gundabad_commander_of_legions_service import build_commander_of_legions_army_evidence

@pytest.fixture(scope="module")
def gundabad(imported_fixture):
    definition, army, army_list = imported_fixture
    # Canonical loader's army rules must be activated for these tests.
    from army_loader import load_army_lists, load_factions
    lists = load_army_lists(load_factions())
    load_army_rules(lists)
    army_list.army_rules = lists["GUNDABAD"].army_rules
    return definition,army,army_list

def analyse(gundabad, definition=True):
    d,a,l=gundabad
    return analyse_imported_army(
        a,l,max(a.total_points(),2000),load_metric_thresholds(),
        **({"gundabad_army_definition": d} if definition else {})
    )

def test_rule_is_registered(gundabad):
    assert sum(r.id=="GUNDABAD_COMMANDER_OF_LEGIONS" for r in gundabad[2].army_rules)==1

def test_import_identifies_azog_as_general(gundabad):
    assert gundabad[0].leader_profile_id=="AZOG_THE_DEFILER"

def test_general_is_resolved_as_a_fielded_model(gundabad):
    d,a,l=gundabad
    ev=build_commander_of_legions_army_evidence(a,l,army_definition=d)
    ids={m.id for m in a.fielded_models()}
    assert ev.general_model_id in ids

def test_azog_receives_master_of_battle_five_plus(gundabad):
    ev=analyse(gundabad)["mechanical_commander_of_legions"]
    assert ev.entitlement.granted
    assert ev.entitlement.granted_rule_id=="MASTER_OF_BATTLE"
    assert ev.entitlement.master_of_battle_target==5

def test_nonqualifying_general_not_granted(gundabad):
    d,a,l=gundabad
    hero=next(m for m in a.fielded_models()
              if m.configured_profile is not None
              and m.profile_id not in ("AZOG_THE_DEFILER","BOLG_SPAWN_OF_AZOG")
              and m.configured_profile.profile.heroic_status is not None
              and m.warband_id is not None)
    altered=replace(d,leader_profile_id=hero.profile_id,leader_warband_id=hero.warband_id)
    ev=build_commander_of_legions_army_evidence(a,l,army_definition=altered)
    assert not ev.entitlement.granted

def test_unknown_general_rejected(gundabad):
    d,a,l=gundabad
    altered=replace(d,leader_profile_id="NOT_FIELDED")
    with pytest.raises(ValueError,match="uniquely resolve"):
        build_commander_of_legions_army_evidence(a,l,army_definition=altered)

def test_wrong_army_rejected(gundabad):
    d,a,l=gundabad
    with pytest.raises(ValueError,match="Army of Gundabad"):
        build_commander_of_legions_army_evidence(
            a,SimpleNamespace(id="DG_PITS",army_rules=l.army_rules),army_definition=d
        )

def test_inactive_rule_rejected(gundabad):
    d,a,l=gundabad
    inactive=SimpleNamespace(id="GUNDABAD",army_rules=[])
    with pytest.raises(ValueError,match="not registered"):
        build_commander_of_legions_army_evidence(a,inactive,army_definition=d)

def test_no_definition_does_not_guess_general(gundabad):
    assert "mechanical_commander_of_legions" not in analyse(gundabad,False)

def test_evidence_diagnostic_only(gundabad):
    ev=analyse(gundabad)["mechanical_commander_of_legions"]
    assert ev.dashboard_score is None and ev.scenario_score is None

def test_existing_scores_preserved(gundabad):
    old,new=analyse(gundabad,False),analyse(gundabad,True)
    for key in ("metric_densities","metric_assessments","battlefield_assessments"):
        assert old[key]==new[key]
