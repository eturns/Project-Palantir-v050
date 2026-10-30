"""DEV-078-ROTN-D2: default service-path acceptance.
Author: Edward Turns (Project Lead)
No score or calibration modifications; entitlement evidence only.
"""
from pathlib import Path

import pytest

from analysis_loader import load_metric_thresholds
from army_loader import load_army_rules
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_analysis_service import analyse_mesbg_list_builder_file
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from rotn_army_magic_service_adapter import analyse_imported_army_with_magic_resistance
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data

FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'rise_of_the_necromancer_all_options.json'


@pytest.fixture(scope='module')
def loaded():
    assert FIXTURE.is_file(), f'Missing existing test fixture: {FIXTURE}'
    profiles, lists, options = load_production_azogs_hunters_data()
    load_army_rules(lists)
    return profiles, lists, options


@pytest.fixture(scope='module')
def imported(loaded):
    profiles, lists, options = loaded
    return import_army_from_mesbg_list_builder(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )


def test_normal_army_service_includes_entitlement(imported):
    _, army, army_list = imported
    result = analyse_imported_army(army, army_list, army.total_points(), load_metric_thresholds())
    inventory = result['mechanical_army_magic_resistance']
    assert inventory.source_rule_id == 'DG_POWER_OF_THE_NECROMANCER'
    assert inventory.eligible_model_ids == tuple(m.id for m in army.fielded_models())
    assert inventory.dashboard_score is inventory.scenario_score is None


def test_opt_in_adapter_is_backward_compatible(imported):
    _, army, army_list = imported
    args = (army, army_list, army.total_points(), load_metric_thresholds())
    standard = analyse_imported_army(*args)
    wrapped = analyse_imported_army_with_magic_resistance(*args)
    assert wrapped['mechanical_army_magic_resistance'] == standard['mechanical_army_magic_resistance']
    assert wrapped['metric_assessments'] == standard['metric_assessments']
    assert wrapped['battlefield_assessments'] == standard['battlefield_assessments']


def test_normal_json_analysis_path_exposes_entitlement(loaded):
    profiles, lists, options = loaded
    result = analyse_mesbg_list_builder_file(
        str(FIXTURE), profiles_by_id=profiles, army_lists_by_id=lists,
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=options,
    )
    inventory = result['analysis']['mechanical_army_magic_resistance']
    assert inventory.army_list_id == 'DG_ROTN'
    assert inventory.source_rule_id == 'DG_POWER_OF_THE_NECROMANCER'
    assert inventory.model_count == result['army'].model_count()


def test_no_resistance_key_for_other_army(loaded):
    profiles, lists, options = loaded
    path = FIXTURE.parent / 'azogs_hunters_all_options.json'
    assert path.is_file()
    _, army, army_list = import_army_from_mesbg_list_builder(
        str(path), profiles_by_id=profiles, army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    result = analyse_imported_army(army, army_list, army.total_points(), load_metric_thresholds())
    assert 'mechanical_army_magic_resistance' not in result
