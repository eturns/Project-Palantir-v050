from scenario_analysis_result import ScenarioAnalysisResult
from scenario_definition import ScenarioPool
from scenario_demand import StrategicDemand
from scenario_demand_analysis import ScenarioDemandAnalysis


def test_scenario_analysis_result_stores_scenario_metadata_score_and_demands():
    demands = (
        ScenarioDemandAnalysis(
            dimension=StrategicDemand.MOBILITY,
            capability=0.8,
            intensity=1.0,
        ),
    )

    result = ScenarioAnalysisResult(
        scenario_id="DOMINATION",
        scenario_name="Domination",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        score=0.85,
        demands=demands,
    )

    assert result.scenario_id == "DOMINATION"
    assert result.scenario_name == "Domination"
    assert result.pool == ScenarioPool.HOLD_OBJECTIVE
    assert result.score == 0.85
    assert result.demands == demands