"""DEV-077-GUN-D3-B: Gundabad fixture through the existing scenario service.

Analysis acceptance only: this fixture need not be tournament legal.
Do not infer battlefield state or recalibrate provisional dashboard metrics.
"""
from math import isfinite
from pathlib import Path

import pytest

from analysis_loader import load_metric_thresholds
from scenario_catalogue import get_official_scenarios
from scenario_analysis_builder import rank_scenario_analysis_results
from services.mesbg_list_analysis_service import analyse_mesbg_list_builder_file
from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "gundabadalloptions.json"


@pytest.fixture(scope="module")
def analysed_gundabad():
    assert FIXTURE.is_file(), f"Missing production fixture: {FIXTURE}"
    profiles, army_lists, options = load_production_azogs_hunters_data()
    result = analyse_mesbg_list_builder_file(
        str(FIXTURE),
        profiles_by_id=profiles,
        army_lists_by_id=army_lists,
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=options,
    )
    return result


def _snapshot(army):
    return (
        army.total_points(),
        tuple((
            getattr(e.configured_profile.profile, "id", None)
            if e.configured_profile is not None
            else getattr(e.siege_engine_profile, "id", None),
            e.quantity,
            e.warband_id,
            tuple(o.id for o in e.configured_profile.selected_options)
            if e.configured_profile is not None else (),
        ) for e in army.entries),
    )


def test_service_imports_gundabad_and_produces_scenarios(analysed_gundabad):
    result = analysed_gundabad
    assert result["definition"].army_list_id == "GUNDABAD"
    assert result["army_list"].id == "GUNDABAD"
    assert result["scenario_analysis_results"] is not None


def test_scenario_catalogue_has_full_unique_coverage(analysed_gundabad):
    rows = analysed_gundabad["scenario_analysis_results"]
    expected = get_official_scenarios()
    ids = [row.scenario_id for row in rows]
    assert len(expected) > 0
    assert len(rows) == len(expected)
    assert len(ids) == len(set(ids))
    assert set(ids) == {s.id for s in expected}


def test_all_scenario_scores_finite_and_bounded(analysed_gundabad):
    for row in analysed_gundabad["scenario_analysis_results"]:
        assert isfinite(float(row.score)), row.scenario_id
        assert 0 <= float(row.score) <= 1, (row.scenario_id, row.score)
        assert row.scenario_name


def test_scenario_demand_evidence_is_finite(analysed_gundabad):
    for row in analysed_gundabad["scenario_analysis_results"]:
        for demand in row.demands:
            assert isfinite(float(demand.capability)), (row.scenario_id, demand)
            assert isfinite(float(demand.intensity)), (row.scenario_id, demand)


def test_scenario_ranking_preserves_set_and_descends(analysed_gundabad):
    rows = analysed_gundabad["scenario_analysis_results"]
    ranked = rank_scenario_analysis_results(rows)
    assert {r.scenario_id for r in ranked} == {r.scenario_id for r in rows}
    assert all(ranked[i].score >= ranked[i + 1].score for i in range(len(ranked) - 1))


def test_analysis_preserves_imported_configuration(analysed_gundabad):
    army = analysed_gundabad["army"]
    before = _snapshot(army)
    assert before[0] > 0
    profiles, lists, options = load_production_azogs_hunters_data()
    rerun = analyse_mesbg_list_builder_file(
        str(FIXTURE),
        profiles_by_id=profiles,
        army_lists_by_id=lists,
        metric_thresholds=load_metric_thresholds(),
        profile_options_by_external_id=options,
    )
    assert before == _snapshot(army) == _snapshot(rerun["army"])
