from dataclasses import dataclass
from enum import Enum


class StrategicDemand(Enum):
    DISTRIBUTED_CONTROL = "distributed_control"
    CONCENTRATED_CONTROL = "concentrated_control"
    MOBILITY = "mobility"
    PROJECTION = "projection"
    OBJECT_INTERACTION = "object_interaction"
    ATTRITION_OUTPUT = "attrition_output"
    KEY_MODEL_PRESSURE = "key_model_pressure"
    KEY_MODEL_PRESERVATION = "key_model_preservation"
    STATE_RESILIENCE = "state_resilience"
    DEPLOYMENT_RECOVERY = "deployment_recovery"


@dataclass(frozen=True)
class ScenarioDemand:
    dimension: StrategicDemand
    intensity: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.dimension,
            StrategicDemand,
        ):
            raise TypeError(
                "dimension must be a StrategicDemand."
            )

        if not 0.0 <= self.intensity <= 1.0:
            raise ValueError(
                "Scenario demand intensity must be between 0.0 and 1.0."
            )

def get_scenario_demand_intensity(
    demands: tuple[ScenarioDemand, ...],
    dimension: StrategicDemand,
) -> float:
    if not isinstance(
        dimension,
        StrategicDemand,
    ):
        raise TypeError(
            "dimension must be a StrategicDemand."
        )

    if not all(
        isinstance(demand, ScenarioDemand)
        for demand in demands
    ):
        raise TypeError(
            "demands must contain only ScenarioDemand values."
        )

    for demand in demands:
        if demand.dimension is dimension:
            return demand.intensity

    return 0.0

def get_scenario_demand_profile(
    demands: tuple[ScenarioDemand, ...],
) -> dict[StrategicDemand, float]:
    if not all(
        isinstance(demand, ScenarioDemand)
        for demand in demands
    ):
        raise TypeError(
            "demands must contain only ScenarioDemand values."
        )

    dimensions = [
        demand.dimension
        for demand in demands
    ]

    if len(dimensions) != len(set(dimensions)):
        raise ValueError(
            "demands cannot contain duplicate strategic dimensions."
        )

    profile = {
        dimension: 0.0
        for dimension in StrategicDemand
    }

    for demand in demands:
        profile[demand.dimension] = demand.intensity

    return profile