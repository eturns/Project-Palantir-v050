"""F4-A1 diagnostic wiring and legacy score invariants."""
from types import SimpleNamespace
import pytest
from army import Army
from services import army_analysis_service as s


class FakeArmy(Army):
    def validate(self, limit):
        return ("ok", limit)

    def analysis_metrics(self):
        return "legacy_metrics"


def patch_pipeline(monkeypatch):
    called = []
    def record(name, result):
        def call(*args, **kwargs):
            called.append((name, args, kwargs))
            return result
        return call
    for name, value in (
        ("calculate_army_metric_densities", "densities"),
        ("calculate_army_offensive_output_density", 0.3),
        ("build_shooting_benchmark_defender", "invalid-benchmark"),
        ("calculate_army_shooting_output_density", 0.4),
        ("normalise_shooting_output_density", 0.5),
        ("calculate_mechanical_defence_diagnostics", "defence"),
        ("build_mobility_integration_contract", "mobility"),
        ("assess_army_metrics", "original_ratings"),
        ("assess_battlefield", "original_scenarios"),
        ("build_army_magic_contract", "magic_diagnostic"),
    ):
        monkeypatch.setattr(s, name, record(name, value))
    return called


def test_magic_is_appended_for_real_army(monkeypatch):
    calls = patch_pipeline(monkeypatch)
    army = FakeArmy()
    result = s.analyse_imported_army(army, object(), 700, object())
    assert result["mechanical_magic"] == "magic_diagnostic"
    assert result["metric_assessments"] == "original_ratings"
    assert result["battlefield_assessments"] == "original_scenarios"
    assert [args[0] for name, args, _ in calls if name == "build_army_magic_contract"] == [army]


def test_magic_not_sent_to_legacy_assessors(monkeypatch):
    calls = patch_pipeline(monkeypatch)
    s.analyse_imported_army(FakeArmy(), object(), 700, "thresholds")
    ratings = next(row for row in calls if row[0] == "assess_army_metrics")
    scenarios = next(row for row in calls if row[0] == "assess_battlefield")
    assert ratings[1] == ("densities", "thresholds")
    assert ratings[2] == {"offence_value": 0.3, "shooting_value": 0.5}
    assert scenarios[1] == ("original_ratings",)
    assert scenarios[2] == {}


def test_legacy_non_army_double_reports_unavailable_magic(monkeypatch):
    calls = patch_pipeline(monkeypatch)
    legacy = SimpleNamespace(validate=lambda limit: (), analysis_metrics=lambda: "legacy")
    result = s.analyse_imported_army(legacy, object(), 700, object())
    assert result["mechanical_magic"] is None
    assert result["metric_assessments"] == "original_ratings"
    assert not any(name == "build_army_magic_contract" for name, _, _ in calls)


def test_real_magic_builder_error_is_not_silenced(monkeypatch):
    patch_pipeline(monkeypatch)
    def bad(army):
        raise ValueError("corrupt magic input")
    monkeypatch.setattr(s, "build_army_magic_contract", bad)
    with pytest.raises(ValueError, match="corrupt magic input"):
        s.analyse_imported_army(FakeArmy(), object(), 700, object())


def test_real_empty_army_produces_diagnostic_contract(monkeypatch):
    patch_pipeline(monkeypatch)
    from mechanical_magic_army_contract import build_army_magic_contract
    monkeypatch.setattr(s, "build_army_magic_contract", build_army_magic_contract)
    result = s.analyse_imported_army(FakeArmy(), object(), 700, object())
    report = result["mechanical_magic"]
    assert report.caster_count == 0
    assert report.dashboard_score is None
    assert report.scenario_score is None
    assert result["metric_assessments"] == "original_ratings"
