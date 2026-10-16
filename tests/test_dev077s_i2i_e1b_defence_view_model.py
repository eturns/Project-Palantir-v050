"""Non-scoring Defence presentation view-model integration tests."""
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from desktop_analysis_view_model import build_desktop_analysis_view_model
from defence_presentation_contract import from_mechanical_diagnostics


def _result(army):
    return {
        "definition": SimpleNamespace(name="Example", points_limit=700),
        "army": army,
        "analysis": {
            "validation_errors": (),
            "metric_assessments": (SimpleNamespace(metric="defence", rating="Strong", value=0.65),),
            "battlefield_assessments": SimpleNamespace(strengths=(), weaknesses=()),
        },
        "scenario_analysis_results": (),
        "evidence_records": (),
    }


def _sample():
    return from_mechanical_diagnostics({
        "combat_density": 2.9270251837875314,
        "combat_survival": 0.5246129752480729,
        "engagements": 3,
    })


def test_non_army_stub_preserves_legacy_metrics():
    vm = build_desktop_analysis_view_model(_result(SimpleNamespace(total_points=lambda: 700)))
    assert vm["defence_presentation"] is None
    assert vm["metrics"] == ({"metric": "Defence", "rating": "Strong", "value": 0.65},)


def test_actual_army_uses_mechanical_adapter(monkeypatch):
    class StubArmy:
        def total_points(self):
            return 700
    monkeypatch.setattr("desktop_analysis_view_model.Army", StubArmy)
    army = StubArmy()
    with patch("desktop_analysis_view_model.build_defence_presentation", return_value=_sample()) as fn:
        vm = build_desktop_analysis_view_model(_result(army))
    fn.assert_called_once_with(army)
    data = vm["defence_presentation"]
    assert data["army_survival_density"]["label"] == "Army Survival Density"
    assert data["army_survival_density"]["value"] == pytest.approx(2.9270251837875314)
    assert data["per_model_resilience"]["label"] == "Per-Model Resilience"
    assert data["per_model_resilience"]["value"] == pytest.approx(0.5246129752480729)
    assert data["per_model_resilience"]["calibrated"] is False
    assert data["benchmark"]["defence"] == 6
    assert data["engagements"] == 3
    assert data["production_score_changed"] is False
    assert vm["metrics"][0]["metric"] == "Defence"


def test_mechanical_errors_not_silently_replaced_by_zero(monkeypatch):
    class StubArmy:
        def total_points(self):
            return 700
    monkeypatch.setattr("desktop_analysis_view_model.Army", StubArmy)
    with patch("desktop_analysis_view_model.build_defence_presentation", side_effect=ValueError("bad army")):
        with pytest.raises(ValueError, match="bad army"):
            build_desktop_analysis_view_model(_result(StubArmy()))
