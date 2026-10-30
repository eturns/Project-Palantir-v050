"""DEV-078-ROTN-D3: real-army standard-path cast contract acceptance."""
from pathlib import Path
from types import SimpleNamespace
import pytest
from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_analysis_service import analyse_mesbg_list_builder_file
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data
from necromancer_cast_sequence import CastDeclaration
from rotn_army_cast_service import DeclaredCastRequest

FIXTURES = Path(__file__).resolve().parent / 'fixtures'

@pytest.fixture(scope='module')
def data():
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    return profiles, lists, options

@pytest.fixture(scope='module')
def rise(data):
    profiles, lists, options = data
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURES / 'rise_of_the_necromancer_all_options.json'),
        profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army, army_list

def assess(rise, **kwargs):
    army, army_list = rise
    return analyse_imported_army(army, army_list, army.total_points(), load_metric_thresholds(), **kwargs)

def test_default_service_exposes_necromancer_contract(rise):
    army, _ = rise
    e = assess(rise)['mechanical_necromancer_cast_sequence']
    assert e.eligible_model_ids == tuple(m.id for m in army.fielded_models() if m.profile_id == 'DG_NEC')
    assert e.permitted_attempts_per_activation == 2
    assert e.assessed_sequences == ()
    assert e.dashboard_score is e.scenario_score is None

def test_normal_json_service_exposes_contract(data):
    profiles, lists, options = data
    r = analyse_mesbg_list_builder_file(
        str(FIXTURES / 'rise_of_the_necromancer_all_options.json'),
        profiles_by_id=profiles, army_lists_by_id=lists,
        metric_thresholds=load_metric_thresholds(), profile_options_by_external_id=options,
    )
    assert r['analysis']['mechanical_necromancer_cast_sequence'].eligible_model_ids

def request(*casts):
    evidence = SimpleNamespace(profile_id='DG_NEC',spell_options=(
        SimpleNamespace(spell_id='TRANSFIX'), SimpleNamespace(spell_id='SAP_WILL')))
    return DeclaredCastRequest(evidence, tuple(casts))

def nec_id(rise):
    return next(m.id for m in rise[0].fielded_models() if m.profile_id == 'DG_NEC')

def test_explicit_distinct_casts_are_checked(rise):
    cid = nec_id(rise)
    e = assess(rise, rotn_cast_requests_by_model_id={cid: request(
        CastDeclaration('TRANSFIX','enemy-a',True),CastDeclaration('SAP_WILL','enemy-b',True))
    })['mechanical_necromancer_cast_sequence']
    assert e.assessed_sequences[0][0] == cid
    assert e.assessed_sequences[0][1].validated

def test_duplicate_enemy_rejected_on_normal_service(rise):
    cid = nec_id(rise)
    with pytest.raises(ValueError, match='same enemy'):
        assess(rise, rotn_cast_requests_by_model_id={cid: request(
            CastDeclaration('TRANSFIX','enemy-a',True),CastDeclaration('SAP_WILL','enemy-a',True))})

def test_wrong_model_rejected(rise):
    with pytest.raises(ValueError, match='fielded Necromancer'):
        assess(rise, rotn_cast_requests_by_model_id={'not-fielded':request()})

def test_score_objects_unchanged(rise):
    before = assess(rise)
    after = assess(rise, rotn_cast_requests_by_model_id={nec_id(rise):request(CastDeclaration('TRANSFIX'))})
    assert before['metric_assessments'] == after['metric_assessments']
    assert before['battlefield_assessments'] == after['battlefield_assessments']
