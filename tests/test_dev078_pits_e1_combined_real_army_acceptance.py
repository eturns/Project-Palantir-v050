"""DEV-078-PITS-E1: combined real-army army-rule acceptance.

Author: Edward Turns (Project Lead)
No production code or frozen scoring changes are required for this stage.
"""
from pathlib import Path
from fractions import Fraction

import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from pits_surprise_attack_service import PitsPriorityPhaseRequest
from pits_thrain_imprisonment_service import PitsThrainTestRequest
from pits_wizard_hunters_service import WizardHuntersStrikeRequest
from rotn_army_resistance_outcomes_service import ResistanceRequest
from shattered_spirit_state import ShatteredSpiritResult

FIXTURE = Path(__file__).parent / 'fixtures/pits_of_dol_guldur_all_options.json'
REQUIRED_RULE_IDS = frozenset({
    'DG_SURPRISE_ATTACK', 'DG_MAGICAL_VOID',
    'DG_THRAINS_IMPRISONMENT', 'DG_WIZARD_HUNTERS',
})


@pytest.fixture(scope='module')
def pits():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list


def model_id(pits, name):
    return next(
        m.id for m in pits[0].fielded_models()
        if m.configured_profile is not None
        and m.configured_profile.profile.name == name
    )


def analysis(pits, **kwargs):
    army, army_list = pits
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **kwargs
    )


def all_requests(pits):
    return {
        'pits_surprise_attack_request': PitsPriorityPhaseRequest(
            azog_alive=True, azog_on_battlefield=True,
            already_used=False, declare_surprise_attack=True,
        ),
        'pits_thrain_test_request': PitsThrainTestRequest(
            first_die=1, second_die=2, intelligence='6+',
            keeper_on_battlefield=True, keeper_distance_inches=6.0,
        ),
        'pits_wizard_hunters_request': WizardHuntersStrikeRequest(
            attacker_model_id=model_id(pits, 'Gundabad Orc Warrior'),
            defender_defence=5, defender_can_cast_magical_powers=True,
        ),
        'rotn_resistance_requests_by_model_id': {
            model_id(pits, 'Gundabad Orc Warrior'): ResistanceRequest(
                cast_highest=4, will_available=0,
            ),
        },
    }


def test_canonical_four_rules_registered_once(pits):
    assert pits[1].id == 'DG_PITS'
    rules = [r.id for r in pits[1].army_rules]
    assert REQUIRED_RULE_IDS <= set(rules)
    assert all(rules.count(rule) == 1 for rule in REQUIRED_RULE_IDS)


def test_one_call_produces_all_four_army_rule_outputs(pits):
    result = analysis(pits, **all_requests(pits))
    for key in (
        'mechanical_pits_surprise_attack',
        'mechanical_pits_thrain_imprisonment',
        'mechanical_pits_wizard_hunters',
        'mechanical_army_magic_resistance',
        'mechanical_army_resistance_outcomes',
    ):
        assert key in result


def test_priority_control_in_combined_analysis(pits):
    r = analysis(pits, **all_requests(pits))['mechanical_pits_surprise_attack']
    assert r.declared and r.used_after_phase
    assert r.priority_winner == 'pits'
    assert r.opposing_heroic_moves_prohibited


def test_thrain_failure_converted_without_doubles_benefit(pits):
    r = analysis(pits, **all_requests(pits))['mechanical_pits_thrain_imprisonment']
    assert r.thrain_counts_as_evil and r.imprisonment_applied
    assert r.original_state.result is ShatteredSpiritResult.OPPONENT_CONTROLLED
    assert r.effective_state.result is ShatteredSpiritResult.NORMAL


def test_magical_void_zero_will_still_resists(pits):
    result = analysis(pits, **all_requests(pits))
    inventory = result['mechanical_army_magic_resistance']
    assert inventory.source_rule_id == 'DG_MAGICAL_VOID'
    assert set(inventory.eligible_model_ids) == {m.id for m in pits[0].fielded_models()}
    key = model_id(pits, 'Gundabad Orc Warrior')
    resistance = dict(result['mechanical_army_resistance_outcomes'].outcomes_by_model_id)[key]
    assert resistance.free_dice == 1 and resistance.will_after_spend == 0
    assert resistance.probability_resisted == pytest.approx(0.5)


def test_wizard_hunters_wound_bonus_in_combined_analysis(pits):
    r = analysis(pits, **all_requests(pits))['mechanical_pits_wizard_hunters']
    assert r.entitled and r.applied_modifier == 1
    assert r.modified_wound_probability > r.baseline_wound_probability


def test_existing_assessments_are_identical(pits):
    baseline = analysis(pits)
    combined = analysis(pits, **all_requests(pits))
    for name in ('validation_errors', 'metrics', 'metric_densities',
                 'metric_assessments', 'battlefield_assessments'):
        assert baseline[name] == combined[name]


def test_no_requests_do_not_invent_battlefield_events(pits):
    result = analysis(pits)
    for name in ('mechanical_pits_surprise_attack',
                 'mechanical_pits_thrain_imprisonment',
                 'mechanical_pits_wizard_hunters',
                 'mechanical_army_resistance_outcomes'):
        assert name not in result
    assert result['mechanical_army_magic_resistance'].source_rule_id == 'DG_MAGICAL_VOID'


def test_all_four_mechanics_remain_uncalibrated(pits):
    result = analysis(pits, **all_requests(pits))
    for key in ('mechanical_pits_surprise_attack',
                'mechanical_pits_thrain_imprisonment',
                'mechanical_pits_wizard_hunters',
                'mechanical_army_magic_resistance',
                'mechanical_army_resistance_outcomes'):
        assert result[key].dashboard_score is None
        assert result[key].scenario_score is None


def test_invalid_wizard_hunter_does_not_silently_score(pits):
    requests = all_requests(pits)
    requests['pits_wizard_hunters_request'] = WizardHuntersStrikeRequest(
        attacker_model_id='not-fielded', defender_defence=5,
        defender_can_cast_magical_powers=True,
    )
    with pytest.raises(ValueError, match='not uniquely fielded'):
        analysis(pits, **requests)
