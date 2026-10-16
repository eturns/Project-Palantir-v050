"""DEV-077S-I2-I-P2-C3-F — presentation/scoring isolation regression.

This asserts that P2 desktop adaptation never changes upstream scenario
objects, legacy metrics, or optimiser candidate scoring. It is deliberately
NOT a claim of numerical equality against the historical DEV-073 baselines.
"""
from copy import deepcopy
from types import SimpleNamespace

import pytest

import desktop_analysis_adapter as adapter
from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_evaluator import evaluate_candidate
from optimiser_objective import OptimiserObjective
from optimiser_ranking import rank_evaluations
from provisional_desktop_view import build_provisional_desktop_view


class ConstantObjective(OptimiserObjective):
    def evaluate(self, candidate):
        return float(candidate.army.total_points())


def _scenario():
    return SimpleNamespace(
        scenario_id="HOLD_GROUND",
        scenario_name="Hold Ground",
        pool=SimpleNamespace(value="matched_play"),
        score=0.731,
        demands=(SimpleNamespace(
            dimension=SimpleNamespace(value="board_control"),
            capability=0.61,
            intensity=0.77,
        ),),
    )


def _raw_result():
    scenario = _scenario()
    return {
        "definition": SimpleNamespace(name="Isolation Fixture", points_limit=700),
        "army": SimpleNamespace(total_points=lambda: 695),
        "analysis": {
            "validation_errors": (),
            "metric_assessments": (SimpleNamespace(
                metric="offence", rating="Strong", value=0.62,
            ),),
            "battlefield_assessments": SimpleNamespace(
                strengths=(), weaknesses=(),
            ),
        },
        "scenario_analysis_results": (scenario,),
        "evidence_records": (),
    }


def test_desktop_adapter_does_not_modify_raw_scenario_or_metric_objects(monkeypatch):
    upstream = _raw_result()
    scenario_before = deepcopy(upstream["scenario_analysis_results"])
    metrics_before = deepcopy(upstream["analysis"]["metric_assessments"])
    monkeypatch.setattr(adapter, "run_analysis_workflow",
                        lambda path, print_report=False: upstream)
    view = adapter.run_analysis("dummy.json")
    assert upstream["scenario_analysis_results"] == scenario_before
    assert upstream["analysis"]["metric_assessments"] == metrics_before
    assert view["scenarios"][0]["score"] == pytest.approx(0.731)
    assert view["scenarios"][0]["demands"][0]["capability"] == pytest.approx(0.61)
    assert view["metrics"][0]["rating"] == "Strong"
    assert view["metrics"][0]["value"] == pytest.approx(0.62)
    assert view["provisional_capabilities"]["display_only"] is True
    assert view["provisional_capabilities"]["production_scoring_changed"] is False


def test_provisional_display_is_not_a_legacy_optimiser_objective():
    objective = ConstantObjective()
    first, second = OptimiserCandidate(Army()), OptimiserCandidate(Army())
    before = (evaluate_candidate(first, objective), evaluate_candidate(second, objective))
    before_order = rank_evaluations(before)
    panel = build_provisional_desktop_view(
        None,
        qualified_measurements={"offence_density": 0.6180555555555556},
        evidence_statuses={"offence_density": "evaluated"},
    )
    after = (evaluate_candidate(first, objective), evaluate_candidate(second, objective))
    assert after == before
    assert rank_evaluations(after) == before_order
    assert panel["production_scoring_changed"] is False
    assert panel["defence_independent_composite_weighting_allowed"] is False
    rows = {r["metric_id"]: r for r in panel["metrics"]}
    assert rows["offence_density"]["rating"] == pytest.approx(0.49777833755014805)
    assert rows["magic"]["rating"] is None


def test_presentation_uses_no_optimiser_or_scenario_service_imports():
    from pathlib import Path
    import provisional_calibration
    import provisional_desktop_view
    for module in (provisional_calibration, provisional_desktop_view):
        source = Path(module.__file__).read_text(encoding="utf-8")
        for token in ("from optimiser", "import optimiser", "from scenario_", "import scenario_"):
            assert token not in source
