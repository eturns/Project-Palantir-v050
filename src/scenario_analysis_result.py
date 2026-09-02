from dataclasses import dataclass

from scenario_definition import ScenarioPool
from scenario_demand_analysis import ScenarioDemandAnalysis


@dataclass(frozen=True)
class ScenarioAnalysisResult:
    scenario_id: str
    scenario_name: str
    pool: ScenarioPool
    score: float
    demands: tuple[ScenarioDemandAnalysis, ...] = ()