from scenario_analysis_report import (
    format_scenario_analysis_report,
    build_scenario_analysis_report
)
from scenario_analysis_result import ScenarioAnalysisResult
from scenario_definition import ScenarioPool
from scenario_demand import StrategicDemand
from scenario_demand_analysis import ScenarioDemandAnalysis

def test_format_scenario_analysis_report_includes_top_and_bottom_sections():
    top = (
        ScenarioAnalysisResult(
            scenario_id="DOMINATION",
            scenario_name="Domination",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.9,
            demands=(
                ScenarioDemandAnalysis(
                    dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                    capability=0.8,
                    intensity=1.0,
                ),
            ),
        ),
    )

    bottom = (
        ScenarioAnalysisResult(
            scenario_id="FOG_OF_WAR",
            scenario_name="Fog of War",
            pool=ScenarioPool.UNIQUE,
            score=0.4,
            demands=(
                ScenarioDemandAnalysis(
                    dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
                    capability=0.3,
                    intensity=1.0,
                ),
            ),
        ),
    )

    report = format_scenario_analysis_report(
        top=top,
        bottom=bottom,
    )

    assert "Top Scenarios" in report
    assert "Bottom Scenarios" in report
    assert "Domination" in report
    assert "Fog of War" in report
    assert "0.900" in report
    assert "0.400" in report
    assert "distributed_control" in report
    assert "key_model_preservation" in report

def test_build_scenario_analysis_report_selects_top_and_bottom_five():
    results = tuple(
        ScenarioAnalysisResult(
            scenario_id=f"SCENARIO_{index}",
            scenario_name=f"Scenario {index}",
            pool=ScenarioPool.UNIQUE,
            score=index / 23,
        )
        for index in range(24)
    )

    report = build_scenario_analysis_report(
        results,
    )

    assert "Top Scenarios" in report
    assert "Bottom Scenarios" in report

    assert "Scenario 23" in report
    assert "Scenario 22" in report
    assert "Scenario 21" in report
    assert "Scenario 20" in report
    assert "Scenario 19" in report

    assert "Scenario 4" in report
    assert "Scenario 3" in report
    assert "Scenario 2" in report
    assert "Scenario 1" in report
    assert "Scenario 0" in report

    assert "Scenario 18" not in report
    assert "Scenario 5" not in report