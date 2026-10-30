"""DEV-078-ROTN-D4 Stage 2: real-army free-Will production acceptance.

Author: Edward Turns (Project Lead)
"""
from pathlib import Path

import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from necromancer_free_will_casting import FundedCastRequest

FIXTURE = Path(__file__).parent / 'fixtures/rise_of_the_necromancer_all_options.json'


@pytest.fixture(scope='module')
def rise():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list


def call(rise, **kw):
    army, army_list = rise
    return analyse_imported_army(
        army, army_list, army.total_points(), load_metric_thresholds(), **kw
    )


def nec_id(rise):
    return next(m.id for m in rise[0].fielded_models() if m.profile_id == 'DG_NEC')


def req(spell, target, spent=1):
    return FundedCastRequest(spell_id=spell, target_id=target, cast_value=4, will_spent=spent)


def test_normal_service_includes_funded_cast_contract(rise):
    model_id = nec_id(rise)
    result = call(rise, rotn_funded_cast_requests_by_model_id={
        model_id: (req('TRANSFIX', 'enemy-1'),)
    })
    report = result['mechanical_necromancer_cast_sequence']
    assert report.funded_sequences[0][0] == model_id
    evidence = report.funded_sequences[0][1]
    assert evidence.casts[0].cast.additional_dice == 1
    assert evidence.casts[0].cast.will_spent == 1
    assert evidence.remaining_will == evidence.initial_will - 1
    assert report.dashboard_score is None and report.scenario_score is None


def test_two_casts_use_shared_will_ledger(rise):
    model_id = nec_id(rise)
    result = call(rise, rotn_funded_cast_requests_by_model_id={model_id: (
        req('TRANSFIX', 'enemy-1'), req('COMPEL', 'enemy-2'),
    )})
    sequence = result['mechanical_necromancer_cast_sequence'].funded_sequences[0][1]
    assert len(sequence.casts) == 2
    assert [item.cast.additional_dice for item in sequence.casts] == [1, 1]
    assert sequence.casts[0].will_after == sequence.casts[1].will_before
    assert sequence.remaining_will == sequence.initial_will - 2


def test_wrong_model_id_rejected(rise):
    with pytest.raises(ValueError, match='fielded Necromancer'):
        call(rise, rotn_funded_cast_requests_by_model_id={
            'INVALID': (req('TRANSFIX', 'enemy-1'),)
        })


def test_duplicate_target_rejected(rise):
    model_id = nec_id(rise)
    with pytest.raises(ValueError, match='same enemy'):
        call(rise, rotn_funded_cast_requests_by_model_id={model_id: (
            req('TRANSFIX', 'enemy-1'), req('COMPEL', 'enemy-1'),
        )})


def test_legacy_score_objects_unchanged(rise):
    model_id = nec_id(rise)
    before = call(rise)
    after = call(rise, rotn_funded_cast_requests_by_model_id={model_id: (
        req('TRANSFIX', 'enemy-1'),
    )})
    assert before['metric_assessments'] == after['metric_assessments']
    assert before['battlefield_assessments'] == after['battlefield_assessments']
    assert before['mechanical_necromancer_cast_sequence'].funded_sequences == ()


def test_existing_cast_contract_still_present(rise):
    assert call(rise)['mechanical_necromancer_cast_sequence'].permitted_attempts_per_activation == 2
