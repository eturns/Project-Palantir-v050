"""DEV-077-GUN-D3-C — real-fixture cross-army analysis stability.

This test checks invariants and in-process contamination, not fixed score
calibration. The existing Stage-4 recalibration remains out of scope.
"""
from math import isfinite
from pathlib import Path

import pytest

from analysis_loader import load_metric_thresholds
from scenario_catalogue import get_official_scenarios
from services.mesbg_list_analysis_service import analyse_mesbg_list_builder_file
from services.mesbg_list_builder_import_service import import_army_from_mesbg_list_builder
from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ARMIES = {
    "gundabad": "gundabadalloptions.json",
    "rise": "rise_of_the_necromancer_all_options.json",
    "pits": "pits_of_dol_guldur_all_options.json",
    "hunters": "azogs_hunters_all_options.json",
    "iron_hills": "iron_hills_army.json",
    "dale": "garrison_of_dale.json",
}


def analyse(key):
    path = FIXTURES / ARMIES[key]
    assert path.is_file(), f"Required fixture missing: {path}"
    profiles, army_lists, options = load_production_azogs_hunters_data()
    return analyse_mesbg_list_builder_file(
        str(path),
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=options,
    )


def army_signature(army):
    return (
        army.total_points(),
        tuple(
            (
                entry.profile.id if entry.configured_profile is not None
                else entry.siege_engine_profile.id,
                entry.quantity,
                entry.warband_id,
                tuple(o.id for o in entry.configured_profile.selected_options)
                if entry.configured_profile is not None else (),
            )
            for entry in army.entries
        ),
    )


def result_signature(result):
    assessments = result["analysis"]["metric_assessments"]
    scenarios = result["scenario_analysis_results"]
    return (
        army_signature(result["army"]),
        tuple((a.metric, float(a.value), a.rating) for a in assessments),
        None if scenarios is None else tuple(
            (r.scenario_id, float(r.score)) for r in scenarios
        ),
    )


@pytest.mark.parametrize("key", ("gundabad", "rise", "pits", "hunters", "dale"))
def test_real_armies_import_and_assess_ten_capabilities(key):
    result = analyse(key)
    assert result["army"].total_points() > 0
    assessments = result["analysis"]["metric_assessments"]
    assert len(assessments) == 10
    assert len({a.metric for a in assessments}) == 10
    for assessment in assessments:
        assert isfinite(float(assessment.value)), (key, assessment.metric)


@pytest.mark.parametrize("key", ("gundabad", "rise", "pits", "hunters"))
def test_evil_armies_have_complete_bounded_scenario_coverage(key):
    scenarios = analyse(key)["scenario_analysis_results"]
    assert scenarios is not None, f"No scenario analysis for {key}"
    expected_ids = {s.id for s in get_official_scenarios()}
    assert len(scenarios) == len(expected_ids)
    assert {s.scenario_id for s in scenarios} == expected_ids
    assert all(isfinite(float(s.score)) and 0 <= s.score <= 1 for s in scenarios)


@pytest.mark.parametrize("key", ("rise", "pits", "hunters", "dale"))
def test_gundabad_analysis_does_not_change_other_armies_in_same_process(key):
    before = result_signature(analyse(key))
    gundabad = analyse("gundabad")
    assert gundabad["army_list"].id == "GUNDABAD"
    after = result_signature(analyse(key))
    assert after == before, f"Unexpected cross-army state contamination: {key}"


def test_gundabad_repeatability_after_other_armies():
    before = result_signature(analyse("gundabad"))
    analyse("hunters")
    analyse("dale")
    after = result_signature(analyse("gundabad"))
    assert after == before


def test_iron_hills_fixture_still_imports_without_assuming_complete_shooting():
    """Import fidelity is separate from full shooting evidence completeness."""
    path = FIXTURES / ARMIES["iron_hills"]
    profiles, army_lists, options = load_production_azogs_hunters_data()
    definition, army, army_list = import_army_from_mesbg_list_builder(
        str(path),
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        profile_options_by_external_id=options,
    )
    assert definition is not None
    assert army.total_points() > 0
    assert army_list is not None


def test_iron_hills_incomplete_ranged_mechanics_are_reported_not_silently_scored():
    """Existing limitation: no false zero or fabricated ranged output."""
    with pytest.raises(
        ValueError,
        match="All ranged weapons must be mechanically complete",
    ):
        analyse("iron_hills")
