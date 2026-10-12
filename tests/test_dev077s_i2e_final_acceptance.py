"""DEV-077S-I2-E final acceptance: real imported army + service isolation.

All fixtures are repository-backed; no fabricated real-army compositions.
Calibration and battlefield-state predictions remain explicitly pending.
"""
import pytest

from courage_integration_contract import build_courage_integration_contract
from courage_cross_army_validation import (
    CourageBenchmark, CourageValidationCase,
    compare_army_courage, validate_courage_report,
)
from projection_capability import build_shooting_benchmark_defender
from services import army_analysis_service as service
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)


@pytest.fixture(scope="module")
def azog_army():
    profiles, lists, options = load_production_azogs_hunters_data()
    _, army, _ = import_army_from_mesbg_list_builder(
        "tests/fixtures/azogs_hunters_all_options.json",
        profiles_by_id=profiles,
        army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army


def test_real_azogs_hunters_courage_contract_is_traceable(azog_army):
    evidence = build_courage_integration_contract(
        azog_army, build_shooting_benchmark_defender()
    )
    assert evidence.model_count == azog_army.model_count() > 0
    assert evidence.army_points == azog_army.total_points() > 0
    assert 0 <= evidence.friendly_reliability.value <= 1
    assert 0 <= evidence.terror_coverage.value <= 1
    assert evidence.expected_denied_charges.value >= 0
    assert evidence.broken_retention is None  # no inferred Broken state
    assert evidence.broken_expected_retained is None
    assert evidence.dashboard_score is None
    assert evidence.scenario_score is None
    assert evidence.calibration_status == "pending"


def test_real_fixture_across_different_enemy_courage_benchmarks(azog_army):
    benchmark = build_shooting_benchmark_defender()
    report = compare_army_courage(
        (CourageValidationCase("azogs_hunters_production_fixture", azog_army),),
        (CourageBenchmark("configured_6plus", benchmark),),
    )
    assert len(report.rows) == 1
    assert validate_courage_report(report) == ()
    assert report.rows[0].evidence.benchmark_attacker_courage == "6+"


def test_legacy_service_assessment_pipeline_unchanged_with_real_army(
    monkeypatch, azog_army
):
    expected_metrics = object()
    expected_battlefield = object()
    densities = object()
    calls = []
    monkeypatch.setattr(
        service, "calculate_army_metric_densities", lambda *_: densities
    )
    monkeypatch.setattr(
        service, "calculate_army_offensive_output_density", lambda *_: 0.61
    )
    monkeypatch.setattr(
        service, "calculate_army_shooting_output_density", lambda **_: 0.27
    )
    monkeypatch.setattr(
        service, "normalise_shooting_output_density", lambda _: 0.33
    )
    monkeypatch.setattr(
        service, "calculate_mechanical_defence_diagnostics",
        lambda _: {"defence": "unchanged"},
    )
    # This test deliberately keeps Mobility independent of Courage.
    monkeypatch.setattr(
        service, "build_mobility_integration_contract",
        lambda _: {"mobility": "unchanged"},
    )
    def assess(actual_densities, thresholds, **kwargs):
        calls.append((actual_densities, thresholds, kwargs))
        return expected_metrics
    monkeypatch.setattr(service, "assess_army_metrics", assess)
    monkeypatch.setattr(
        service, "assess_battlefield", lambda _: expected_battlefield
    )

    thresholds = object()
    result = service.analyse_imported_army(
        azog_army, object(), max(2000, azog_army.total_points()), thresholds
    )
    assert result["mechanical_courage"] is not None
    assert result["mechanical_courage"].dashboard_score is None
    assert result["mechanical_courage"].scenario_score is None
    assert result["mechanical_defence"] == {"defence": "unchanged"}
    assert result["mechanical_mobility"] == {"mobility": "unchanged"}
    assert result["metric_assessments"] is expected_metrics
    assert result["battlefield_assessments"] is expected_battlefield
    assert calls == [
        (densities, thresholds, {
            "offence_value": 0.61,
            "shooting_value": 0.33,
        }),
    ]


def test_service_courage_is_not_piped_into_existing_scenario_inputs(
    monkeypatch, azog_army
):
    baseline = object()
    changed = object()
    monkeypatch.setattr(service, "calculate_army_metric_densities",
                        lambda *_: baseline)
    monkeypatch.setattr(service, "calculate_army_offensive_output_density",
                        lambda *_: 0.2)
    monkeypatch.setattr(service, "calculate_army_shooting_output_density",
                        lambda **_: 0.4)
    monkeypatch.setattr(service, "normalise_shooting_output_density",
                        lambda _: 0.6)
    monkeypatch.setattr(service, "calculate_mechanical_defence_diagnostics",
                        lambda _: None)
    monkeypatch.setattr(service, "build_mobility_integration_contract",
                        lambda _: None)
    monkeypatch.setattr(service, "build_courage_integration_contract",
                        lambda *_: changed)
    monkeypatch.setattr(service, "assess_army_metrics",
                        lambda densities, thresholds, **kwargs: (
                            densities, thresholds, kwargs
                        ))
    monkeypatch.setattr(service, "assess_battlefield",
                        lambda assessment: assessment)
    result = service.analyse_imported_army(
        azog_army, object(), max(2000, azog_army.total_points()), object()
    )
    assert result["mechanical_courage"] is changed
    assert result["metric_assessments"][0] is baseline
    assert result["metric_assessments"][2] == {
        "offence_value": 0.2, "shooting_value": 0.6
    }
    assert result["battlefield_assessments"] is result["metric_assessments"]
