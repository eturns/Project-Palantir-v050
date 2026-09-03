from types import SimpleNamespace

from reporting.text_analysis_report import (
    print_text_analysis_report,
)
from scenario_analysis_result import ScenarioAnalysisResult
from scenario_definition import ScenarioPool


class TestArmy:
    def total_points(self):
        return 700


def test_text_analysis_report_prints_scenario_analysis(
    capsys,
):
    result = {
        "definition": SimpleNamespace(
            name="Rise of the Necromancer",
            points_limit=700,
        ),
        "army": TestArmy(),
        "analysis": {
            "validation_errors": [],
            "battlefield_assessments": SimpleNamespace(
                strengths=[],
                weaknesses=[],
            ),
        },
        "scenario_analysis_results": (
            ScenarioAnalysisResult(
                scenario_id="DOMINATION",
                scenario_name="Domination",
                pool=ScenarioPool.HOLD_OBJECTIVE,
                score=1.0,
            ),
            ScenarioAnalysisResult(
                scenario_id="LEAD_FROM_THE_FRONT",
                scenario_name="Lead from the Front",
                pool=ScenarioPool.UNIQUE,
                score=0.302,
            ),
        ),
    }

    print_text_analysis_report(
        result,
    )

    output = capsys.readouterr().out

    assert "========== SCENARIO ANALYSIS ==========" in output
    assert "Top Scenarios" in output
    assert "Domination" in output
    assert "Bottom Scenarios" in output
    assert "Lead from the Front" in output