"""DEV-077S-I2-D-E1: Mobility integration cannot modify assessment outputs."""
from types import SimpleNamespace
from services import army_analysis_service as service


def setup(monkeypatch):
    army = SimpleNamespace(validate=lambda limit: [], analysis_metrics=lambda: object())
    densities = SimpleNamespace(mobility=2.39)
    ratings, battlefield, diagnostics = object(), object(), object()
    calls = []
    monkeypatch.setattr(service, "calculate_army_metric_densities", lambda *_: densities)
    monkeypatch.setattr(service, "calculate_army_offensive_output_density", lambda *_: 0.61)
    monkeypatch.setattr(service, "calculate_army_shooting_output_density", lambda **_: 0.27)
    monkeypatch.setattr(service, "build_shooting_benchmark_defender", lambda: object())
    monkeypatch.setattr(service, "normalise_shooting_output_density", lambda _: 0.33)
    monkeypatch.setattr(service, "calculate_mechanical_defence_diagnostics", lambda _: diagnostics)
    monkeypatch.setattr(service, "build_mobility_integration_contract", lambda _: diagnostics)
    def assess(d, t, **kw):
        calls.append((d, t, kw))
        return ratings
    monkeypatch.setattr(service, "assess_army_metrics", assess)
    monkeypatch.setattr(service, "assess_battlefield", lambda _: battlefield)
    return army, densities, ratings, battlefield, diagnostics, calls


def test_mechanical_mobility_diagnostic_is_exposed(monkeypatch):
    army, densities, ratings, battlefield, diagnostics, calls = setup(monkeypatch)
    result = service.analyse_imported_army(army, object(), 700, object())
    assert result["mechanical_mobility"] is diagnostics
    assert result["mechanical_defence"] is diagnostics
    assert result["metric_densities"] is densities


def test_mobility_cannot_override_assessments_or_legacy_density(monkeypatch):
    army, densities, ratings, battlefield, diagnostics, calls = setup(monkeypatch)
    thresholds = object()
    result = service.analyse_imported_army(army, object(), 700, thresholds)
    assert result["metric_assessments"] is ratings
    assert result["battlefield_assessments"] is battlefield
    assert densities.mobility == 2.39
    assert len(calls) == 1
    assert calls[0] == (densities, thresholds, {"offence_value": 0.61, "shooting_value": 0.33})


def test_mobility_contract_has_no_production_score(monkeypatch):
    army, *_ = setup(monkeypatch)
    contract = SimpleNamespace(dashboard_score=None, scenario_score=None, calibration_status="pending")
    monkeypatch.setattr(service, "build_mobility_integration_contract", lambda _: contract)
    result = service.analyse_imported_army(army, object(), 700, object())
    assert result["mechanical_mobility"].dashboard_score is None
    assert result["mechanical_mobility"].scenario_score is None
    assert result["mechanical_mobility"].calibration_status == "pending"
