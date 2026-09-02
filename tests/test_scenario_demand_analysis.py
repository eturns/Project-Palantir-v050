from scenario_demand import StrategicDemand
from scenario_demand_analysis import ScenarioDemandAnalysis


def test_scenario_demand_analysis_stores_dimension_capability_and_intensity():
    analysis = ScenarioDemandAnalysis(
        dimension=StrategicDemand.MOBILITY,
        capability=0.8,
        intensity=1.0,
    )

    assert analysis.dimension == StrategicDemand.MOBILITY
    assert analysis.capability == 0.8
    assert analysis.intensity == 1.0