"""DEV-078-PITS-D2 Wizard Hunters real-army service acceptance.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path
from types import SimpleNamespace
from fractions import Fraction
import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from pits_wizard_hunters_service import WizardHuntersStrikeRequest, build_pits_wizard_hunters_evidence

FIXTURE = Path(__file__).parent / "fixtures/pits_of_dol_guldur_all_options.json"

@pytest.fixture(scope="module")
def pits():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list

def get_model_id(pits, name):
    return next(m.id for m in pits[0].fielded_models()
                if m.configured_profile is not None and m.configured_profile.profile.name == name)

def req(pits, name="Gundabad Orc Warrior", **kw):
    opts = dict(attacker_model_id=get_model_id(pits,name),
                defender_defence=5, defender_can_cast_magical_powers=True)
    opts.update(kw)
    return WizardHuntersStrikeRequest(**opts)

def analyse(pits, request=None):
    army, army_list = pits
    kwargs = {} if request is None else {"pits_wizard_hunters_request":request}
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **kwargs
    )

def test_real_rule_registration(pits):
    assert sum(r.id == "DG_WIZARD_HUNTERS" for r in pits[1].army_rules) == 1

@pytest.mark.parametrize("name", ["Gundabad Orc Warrior","Hunter Orc Warrior"])
def test_eligible_orc_warriors(pits,name):
    ev = analyse(pits, req(pits,name))["mechanical_pits_wizard_hunters"]
    assert ev.entitled and ev.applied_modifier == 1
    assert ev.modified_wound_probability > ev.baseline_wound_probability

def test_orc_hero_not_eligible(pits):
    ev = analyse(pits, req(pits,"Gundabad Orc Captain"))["mechanical_pits_wizard_hunters"]
    assert not ev.entitled and ev.applied_modifier == 0

def test_enemy_non_caster_ineligible(pits):
    ev = analyse(pits, req(pits,defender_can_cast_magical_powers=False))["mechanical_pits_wizard_hunters"]
    assert not ev.entitled

def test_shooting_attack_ineligible(pits):
    ev = analyse(pits, req(pits,is_melee_strike=False))["mechanical_pits_wizard_hunters"]
    assert not ev.entitled

def test_unknown_attacker_rejected(pits):
    with pytest.raises(ValueError,match="not uniquely fielded"):
        analyse(pits, WizardHuntersStrikeRequest("NOT_IN_ARMY",5,True))

def test_inactive_rule_rejected(pits):
    a, l = pits
    inactive = SimpleNamespace(id="DG_PITS",army_rules=[r for r in l.army_rules if r.id != "DG_WIZARD_HUNTERS"])
    with pytest.raises(ValueError,match="active Wizard Hunters"):
        build_pits_wizard_hunters_evidence(a,inactive,request=req(pits))

def test_no_request_preserves_service_contract(pits):
    assert "mechanical_pits_wizard_hunters" not in analyse(pits)

def test_scoring_unchanged(pits):
    before, after = analyse(pits),analyse(pits,req(pits))
    for k in ("metric_assessments","battlefield_assessments","metric_densities"):
        assert before[k] == after[k]

def test_evidence_not_calibrated(pits):
    ev = analyse(pits,req(pits))["mechanical_pits_wizard_hunters"]
    assert ev.dashboard_score is None and ev.scenario_score is None
