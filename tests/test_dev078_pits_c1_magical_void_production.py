"""DEV-078-PITS-C1: real-army Magical Void acceptance.

Author: Edward Turns (Project Lead)
No scoring/calibration changes; reuses DEV-078-ROTN resistance contracts.
"""
from pathlib import Path
from types import SimpleNamespace

import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from rotn_army_magic_service_adapter import build_army_magic_resistance_inventory
from rotn_army_resistance_outcomes_service import ResistanceRequest

FIXTURE = Path(__file__).parent / 'fixtures/pits_of_dol_guldur_all_options.json'


@pytest.fixture(scope='module')
def pits():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list


def analyse(pits, **kwargs):
    army, army_list = pits
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **kwargs
    )


def test_magical_void_registered_in_real_pits_army(pits):
    _, army_list = pits
    assert army_list.id == 'DG_PITS'
    assert sum(rule.id == 'DG_MAGICAL_VOID' for rule in army_list.army_rules) == 1


def test_all_fielded_friendly_models_get_entitlement(pits):
    army, army_list = pits
    inventory = build_army_magic_resistance_inventory(army, army_list)
    assert inventory.source_rule_id == 'DG_MAGICAL_VOID'
    assert inventory.model_count > 0
    assert set(inventory.eligible_model_ids) == {m.id for m in army.fielded_models()}


def test_normal_service_exposes_magical_void_inventory(pits):
    result = analyse(pits)
    evidence = result['mechanical_army_magic_resistance']
    assert evidence.source_rule_id == 'DG_MAGICAL_VOID'
    assert evidence.dashboard_score is None
    assert 'mechanical_army_resistance_outcomes' not in result


def test_zero_will_still_grants_free_resist_die(pits):
    model_id = pits[0].fielded_models()[0].id
    result = analyse(pits, rotn_resistance_requests_by_model_id={
        model_id: ResistanceRequest(cast_highest=4, will_available=0),
    })
    evidence = result['mechanical_army_resistance_outcomes']
    assert evidence.source_rule_id == 'DG_MAGICAL_VOID'
    outcome = dict(evidence.outcomes_by_model_id)[model_id]
    assert (outcome.free_dice, outcome.dice_total, outcome.will_after_spend) == (1, 1, 0)
    assert outcome.probability_resisted == pytest.approx(.5)


def test_paid_and_free_will_not_double_counted(pits):
    model_id = pits[0].fielded_models()[0].id
    result = analyse(pits, rotn_resistance_requests_by_model_id={
        model_id: ResistanceRequest(cast_highest=4, will_available=3, will_spent=2, hero=True),
    })
    outcome = dict(result['mechanical_army_resistance_outcomes'].outcomes_by_model_id)[model_id]
    assert (outcome.free_dice, outcome.dice_total, outcome.will_after_spend) == (1, 3, 1)
    assert outcome.probability_resisted == pytest.approx(.875)
    assert outcome.expected_hero_will_refund == pytest.approx(2/6)


def test_inactive_magical_void_does_not_grant_free_die(pits):
    from rotn_army_resistance_outcomes_service import build_army_resistance_outcomes
    army, army_list = pits
    inactive = SimpleNamespace(id='DG_PITS', army_rules=[
        rule for rule in army_list.army_rules if rule.id != 'DG_MAGICAL_VOID'
    ])
    model_id = army.fielded_models()[0].id
    evidence = build_army_resistance_outcomes(
        army, inactive, requests_by_model_id={
            model_id: ResistanceRequest(cast_highest=4, will_available=0)
        }
    )
    assert evidence.source_rule_id is None
    assert dict(evidence.outcomes_by_model_id)[model_id].probability_resisted == 0


def test_scores_unchanged_by_declared_resistance(pits):
    model_id = pits[0].fielded_models()[0].id
    before = analyse(pits)
    after = analyse(pits, rotn_resistance_requests_by_model_id={
        model_id: ResistanceRequest(cast_highest=6, will_available=0)
    })
    for key in ('metric_densities', 'metric_assessments', 'battlefield_assessments'):
        assert before[key] == after[key]
