"""DEV-077-GUN-D3-A: Real Gundabad fixture through Palantir capability analysis.

This is analyser acceptance, not a tournament army-legality test.
Mechanical diagnostics are evidence, not recalibrated dashboard scores.
"""
from math import isfinite
from pathlib import Path

import pytest

from analysis_loader import load_metric_thresholds
from metric_constants import METRIC_NAMES
from services.army_analysis_service import analyse_imported_army
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import load_production_azogs_hunters_data

FIXTURE = Path(__file__).resolve().parent / 'fixtures' / 'gundabadalloptions.json'


@pytest.fixture(scope='module')
def gundabad_analysis():
    profiles, army_lists, options = load_production_azogs_hunters_data()
    assert FIXTURE.is_file(), f'Gundabad all-options fixture missing: {FIXTURE}'
    definition, army, army_list = import_army_from_mesbg_list_builder(
        str(FIXTURE),
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=options,
    )
    # Do not impose a competition points cap on this coverage fixture.
    result = analyse_imported_army(
        army, army_list, None, load_metric_thresholds()
    )
    return definition, army, army_list, result


def test_gundabad_import_reaches_analysis_service(gundabad_analysis):
    definition, army, army_list, result = gundabad_analysis
    assert definition.army_list_id == 'GUNDABAD'
    assert army_list.id == 'GUNDABAD'
    assert army.total_points() > 0
    assert isinstance(result, dict)


def test_all_ten_metric_assessments_present(gundabad_analysis):
    assessments = gundabad_analysis[3]['metric_assessments']
    assert {entry.metric for entry in assessments} == set(METRIC_NAMES)
    assert len(assessments) == len(METRIC_NAMES) == 10


def test_capability_assessments_are_finite(gundabad_analysis):
    for item in gundabad_analysis[3]['metric_assessments']:
        assert isfinite(float(item.value)), (item.metric, item.value)


def test_mechanical_diagnostics_keys_available(gundabad_analysis):
    result = gundabad_analysis[3]
    for key in (
        'mechanical_defence', 'mechanical_mobility',
        'mechanical_courage', 'mechanical_magic_completeness',
    ):
        assert key in result, key
    # Some contracts may explicitly report incomplete evidence; no fabricated zero.
    assert result['mechanical_magic_completeness'] is not None


def test_analysis_does_not_mutate_army_composition(gundabad_analysis):
    _, army, _, result = gundabad_analysis
    before = tuple((e.profile.id if e.configured_profile is not None else e.siege_engine_profile.id,
                    e.quantity, e.warband_id) for e in army.entries)
    analyse_imported_army(army, gundabad_analysis[2], None, load_metric_thresholds())
    after = tuple((e.profile.id if e.configured_profile is not None else e.siege_engine_profile.id,
                   e.quantity, e.warband_id) for e in army.entries)
    assert before == after
