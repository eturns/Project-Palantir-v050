"""DEV-077S-I2-E-B5-D3: diagnostic-only service integration.

Updated F4-A1 to expect the new diagnostic-only mechanical_magic service key.
"""
from types import SimpleNamespace
import pytest

from services import army_analysis_service as service
from army import Army
from configured_profile import ConfiguredProfile
from profiles import Profile

BENCHMARK = ConfiguredProfile(profile=Profile(
    id="B5D3_BENCHMARK", name="B5D3 Benchmark", points=0,
    movement=6, fight=4, shooting="4+", strength=4, defence=6,
    attacks=1, wounds=1, courage="6+", intelligence="6+",
    might=0, will=0, fate=0, max_in_army=0,
))


class FakeArmy(Army):
    def __init__(self):
        super().__init__()

    def validate(self, limit):
        return ("validation", limit)

    def analysis_metrics(self):
        return "metrics"


def setup_dependencies(monkeypatch, *, courage="courage-evidence"):
    calls = []
    def record(name, result):
        def wrapper(*args, **kwargs):
            calls.append((name, args, kwargs))
            return result
        return wrapper

    monkeypatch.setattr(service, "calculate_army_metric_densities", record("densities", "densities"))
    monkeypatch.setattr(service, "calculate_army_offensive_output_density", record("offence", 0.3))
    monkeypatch.setattr(service, "build_shooting_benchmark_defender", record("benchmark", BENCHMARK))
    monkeypatch.setattr(service, "calculate_army_shooting_output_density", record("shooting", 0.4))
    monkeypatch.setattr(service, "normalise_shooting_output_density", record("normalise", 0.5))
    monkeypatch.setattr(service, "calculate_mechanical_defence_diagnostics", record("defence", "defence-evidence"))
    monkeypatch.setattr(service, "build_mobility_integration_contract", record("mobility", "mobility-evidence"))
    monkeypatch.setattr(service, "build_courage_integration_contract", record("courage", courage))
    monkeypatch.setattr(service, "build_army_magic_contract", record("magic", "magic-evidence"))
    monkeypatch.setattr(service, "assess_army_metrics", record("metric-assessment", "unchanged-metric-scores"))
    monkeypatch.setattr(service, "assess_battlefield", record("battlefield", "unchanged-scenario-scores"))
    return calls


def analyse(monkeypatch, *, courage="courage-evidence"):
    calls = setup_dependencies(monkeypatch, courage=courage)
    army = FakeArmy()
    result = service.analyse_imported_army(
        army, "army-list", 700, "metric-thresholds"
    )
    return calls, army, result


def test_courage_key_is_returned(monkeypatch):
    _, _, result = analyse(monkeypatch)
    assert result["mechanical_courage"] == "courage-evidence"


def test_existing_service_keys_and_values_remain_unchanged(monkeypatch):
    _, _, result = analyse(monkeypatch)
    assert result["mechanical_magic_completeness"].is_complete
    assert result == {
        "validation_errors": ("validation", 700),
        "metrics": "metrics",
        "metric_densities": "densities",
        "metric_assessments": "unchanged-metric-scores",
        "battlefield_assessments": "unchanged-scenario-scores",
        "mechanical_defence": "defence-evidence",
        "mechanical_mobility": "mobility-evidence",
        "mechanical_courage": "courage-evidence",
        "mechanical_magic": "magic-evidence",
        "mechanical_magic_completeness": result["mechanical_magic_completeness"],
    }


def test_courage_receives_same_army_and_configured_benchmark(monkeypatch):
    calls, army, _ = analyse(monkeypatch)
    invoked = [c for c in calls if c[0] == "courage"]
    assert len(invoked) == 1
    assert invoked[0][1] == (army, BENCHMARK)
    assert invoked[0][2] == {}


def test_courage_not_passed_to_metric_assessment(monkeypatch):
    calls, _, _ = analyse(monkeypatch)
    item = next(c for c in calls if c[0] == "metric-assessment")
    assert item[1] == ("densities", "metric-thresholds")
    assert item[2] == {"offence_value": 0.3, "shooting_value": 0.5}
    assert "courage-evidence" not in repr(item)


def test_battlefield_depends_only_on_legacy_metric_assessment(monkeypatch):
    calls, _, _ = analyse(monkeypatch)
    item = next(c for c in calls if c[0] == "battlefield")
    assert item[1] == ("unchanged-metric-scores",)
    assert item[2] == {}


def test_courage_diagnostic_remains_optional_to_legacy_outputs(monkeypatch):
    _, _, result = analyse(monkeypatch, courage=None)
    assert result["mechanical_courage"] is None
    assert result["metric_assessments"] == "unchanged-metric-scores"
    assert result["battlefield_assessments"] == "unchanged-scenario-scores"


def test_no_new_score_arguments_passed_to_old_assessors(monkeypatch):
    calls, _, _ = analyse(monkeypatch)
    assessments = [item for item in calls if item[0] in ("metric-assessment", "battlefield")]
    assert len(assessments) == 2
    assert all("mechanical_courage" not in repr(item) for item in assessments)


def test_service_preserves_existing_validation(monkeypatch):
    _, _, result = analyse(monkeypatch)
    assert result["validation_errors"] == ("validation", 700)


def test_legacy_mock_without_army_entries_has_unavailable_courage(monkeypatch):
    calls = setup_dependencies(monkeypatch)
    mock = SimpleNamespace(
        validate=lambda limit: (),
        analysis_metrics=lambda: "metrics",
    )
    result = service.analyse_imported_army(mock, object(), 700, object())
    assert result["mechanical_courage"] is None
    assert result["mechanical_magic"] is None
    assert result["metric_assessments"] == "unchanged-metric-scores"
    assert not any(name == "courage" for name, args, kwargs in calls)


def test_real_army_with_mocked_invalid_benchmark_has_unavailable_courage(monkeypatch):
    calls = setup_dependencies(monkeypatch)
    monkeypatch.setattr(service, "build_shooting_benchmark_defender", lambda: "mock")
    result = service.analyse_imported_army(FakeArmy(), object(), 700, object())
    assert result["mechanical_courage"] is None
    assert result["battlefield_assessments"] == "unchanged-scenario-scores"
    assert not any(name == "courage" for name, args, kwargs in calls)
