from dataclasses import dataclass

from scenario_demand import StrategicDemand


@dataclass(frozen=True)
class ScenarioDemandAnalysis:
    dimension: StrategicDemand
    capability: float
    intensity: float