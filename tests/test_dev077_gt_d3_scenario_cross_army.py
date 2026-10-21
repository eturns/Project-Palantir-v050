"""DEV-077-GT-D3: Goblin-town scenario coverage and cross-army stability.

Read-only; no recalibration, no fixed ranking requirements. Requires the
700-point Goblin-town fixture and existing Gundabad/Hunters test fixtures.
"""
from math import isfinite
from pathlib import Path

import pytest

from analysis_loader import load_metric_thresholds
from metric_constants import METRIC_NAMES
from scenario_catalogue import get_official_scenarios
from scenario_analysis_builder import rank_scenario_analysis_results
from services.mesbg_list_analysis_service import analyse_mesbg_list_builder_file
from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ARMIES = {
    "horde": "goblin_town_700_horde.json",
    "gundabad": "gundabadalloptions.json",
    "hunters": "azogs_hunters_all_options.json",
    "pits": "pits_of_dol_guldur_all_options.json",
}


def analyse(name):
    path = FIXTURES / ARMIES[name]
    assert path.is_file(), f"Missing required fixture: {path}"
    profiles, lists, options = load_production_azogs_hunters_data()
    return analyse_mesbg_list_builder_file(
        str(path),
        profiles_by_id=profiles,
        army_lists_by_id=lists,
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=options,
    )


def signature(result):
    army = result["army"]
    assessments = result["analysis"]["metric_assessments"]
    scenarios = result["scenario_analysis_results"]
    return (
        army.total_points(),
        tuple((e.profile_id if hasattr(e, "profile_id") else e.profile.id,
               e.quantity, e.warband_id) for e in army.entries),
        tuple((a.metric, float(a.value), a.rating) for a in assessments),
        tuple((s.scenario_id, float(s.score)) for s in scenarios),
    )


@pytest.fixture(scope="module")
def horde():
    return analyse("horde")


def test_horde_is_700_points_and_79_models(horde):
    assert horde["army"].total_points() == 700
    assert horde["army"].model_count() == 79


def test_horde_has_all_ten_legacy_assessments(horde):
    entries = horde["analysis"]["metric_assessments"]
    assert len(entries) == len(METRIC_NAMES) == 10
    assert {entry.metric for entry in entries} == set(METRIC_NAMES)
    assert all(isfinite(float(entry.value)) for entry in entries)


def test_complete_official_scenario_catalogue(horde):
    scenarios = horde["scenario_analysis_results"]
    assert scenarios is not None
    expected = {s.id for s in get_official_scenarios()}
    ids = [s.scenario_id for s in scenarios]
    assert len(scenarios) == len(expected)
    assert set(ids) == expected
    assert len(ids) == len(set(ids))


def test_scenario_scores_and_demand_inputs_are_finite(horde):
    for scenario in horde["scenario_analysis_results"]:
        assert scenario.scenario_name
        assert isfinite(float(scenario.score))
        assert 0 <= scenario.score <= 1
        for demand in scenario.demands:
            assert isfinite(float(demand.capability))
            assert isfinite(float(demand.intensity))


def test_ranking_is_monotonic_without_forcing_specific_winners(horde):
    scenarios = horde["scenario_analysis_results"]
    ranked = rank_scenario_analysis_results(scenarios)
    assert {s.scenario_id for s in ranked} == {s.scenario_id for s in scenarios}
    assert all(ranked[i].score >= ranked[i + 1].score
               for i in range(len(ranked) - 1))


@pytest.mark.parametrize("other", ("gundabad", "hunters", "pits"))
def test_other_army_results_unchanged_after_horde(other):
    before = signature(analyse(other))
    _ = analyse("horde")
    after = signature(analyse(other))
    assert before == after, f"Horde analysis altered {other} results"


def test_horde_repeatable_after_other_armies():
    before = signature(analyse("horde"))
    _ = analyse("gundabad")
    _ = analyse("hunters")
    after = signature(analyse("horde"))
    assert before == after


def test_scenario_comparison_is_descriptive_not_a_calibration(horde, capsys):
    scenarios = rank_scenario_analysis_results(horde["scenario_analysis_results"])
    print("\nGT-D3 HORDE SCENARIO REPORT (existing scenario scoring; not recalibrated)")
    print("Top five:")
    for s in scenarios[:5]:
        print(f"  {s.scenario_name:<32} {float(s.score):.3f}")
    print("Bottom five:")
    for s in scenarios[-5:]:
        print(f"  {s.scenario_name:<32} {float(s.score):.3f}")
    assert len(scenarios) >= 10
