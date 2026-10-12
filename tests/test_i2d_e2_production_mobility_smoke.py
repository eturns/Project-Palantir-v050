"""DEV-077S-I2-D-E2: real imported army and legacy-output isolation.

Uses existing production Azog's Hunters fixture/loader, not a mock Army.
Does not alter production scores, data, or UI.
"""
import pytest

from tests.test_azogs_hunters_json_import_integration import (
    load_production_azogs_hunters_data,
)
from services.mesbg_list_builder_import_service import (
    import_army_from_mesbg_list_builder,
)
from services import army_analysis_service as service
from mobility_integration_contract import build_mobility_integration_contract

FIXTURE = "tests/fixtures/azogs_hunters_all_options.json"


def imported_army():
    profiles, lists, options = load_production_azogs_hunters_data()
    _, army, _ = import_army_from_mesbg_list_builder(
        FIXTURE,
        profiles_by_id=profiles,
        army_lists_by_id=lists,
        profile_options_by_external_id=options,
    )
    return army


def test_real_import_mobility_contract_has_traceable_values():
    army = imported_army()
    contract = build_mobility_integration_contract(army)
    assert contract.model_count == army.model_count() > 0
    assert contract.army_points == army.total_points() > 0
    assert contract.open_ground.value > 0
    assert 0 <= contract.difficult_terrain.value <= contract.open_ground.value
    assert 0 <= contract.terrain_retention.value <= 1
    assert contract.dashboard_score is None
    assert contract.scenario_score is None
    assert contract.calibration_status == "pending"


def test_real_army_service_mobility_does_not_change_assessment_inputs(monkeypatch):
    army = imported_army()
    # The remaining analysis dependencies are mocked to isolate exactly the
    # integration boundary while using real army entries for mechanical Mobility.
    original = service.build_mobility_integration_contract
    expected = original(army)
    densities = object()
    existing_assessments = object()
    existing_battlefield = object()
    calls = []
    monkeypatch.setattr(service, "calculate_army_metric_densities", lambda *_: densities)
    monkeypatch.setattr(service, "calculate_army_offensive_output_density", lambda *_: 0.61)
    monkeypatch.setattr(service, "calculate_army_shooting_output_density", lambda **_: 0.27)
    monkeypatch.setattr(service, "build_shooting_benchmark_defender", lambda: object())
    monkeypatch.setattr(service, "normalise_shooting_output_density", lambda _: 0.33)
    monkeypatch.setattr(service, "calculate_mechanical_defence_diagnostics", lambda _: {"preserved": True})
    def assess(density, thresholds, **kwargs):
        calls.append((density, thresholds, kwargs))
        return existing_assessments
    monkeypatch.setattr(service, "assess_army_metrics", assess)
    monkeypatch.setattr(service, "assess_battlefield", lambda _: existing_battlefield)

    thresholds = object()
    result = service.analyse_imported_army(
        army, army_list=object(), points_limit=max(2000, army.total_points()),
        metric_thresholds=thresholds,
    )
    assert result["mechanical_mobility"] == expected
    assert result["mechanical_defence"] == {"preserved": True}
    assert result["metric_assessments"] is existing_assessments
    assert result["battlefield_assessments"] is existing_battlefield
    assert calls == [(densities, thresholds, {"offence_value": 0.61, "shooting_value": 0.33})]
