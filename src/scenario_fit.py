from dataclasses import dataclass
from scenario_demand import (
    ScenarioDemand,
    StrategicDemand,
)
from scenario_definition import ScenarioDefinition
from scenario_capability import ScenarioCapabilityProfile

@dataclass(frozen=True)
class ScenarioFitResult:
    score: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "Scenario fit score must be between 0.0 and 1.0."
            )

def calculate_scenario_fit(
    demands: tuple[ScenarioDemand, ...],
    capabilities: dict[StrategicDemand, float],
) -> ScenarioFitResult:
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

    if not all(
        isinstance(dimension, StrategicDemand)
        for dimension in capabilities
    ):
        raise TypeError(
            "capabilities keys must be StrategicDemand values."
        )

    for value in capabilities.values():
        if (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        ):
            raise TypeError(
                "Capability values must be int or float."
            )

        if not 0.0 <= value <= 1.0:
            raise ValueError(
                "Capability values must be between 0.0 and 1.0."
            )

    if not demands:
        return ScenarioFitResult(
            score=1.0,
        )

    total_demand = sum(
        demand.intensity
        for demand in demands
    )

    if total_demand == 0.0:
        return ScenarioFitResult(
            score=1.0,
        )

    matched_demand = sum(
        min(
            capabilities.get(
                demand.dimension,
                0.0,
            ),
            demand.intensity,
        )
        for demand in demands
    )

    return ScenarioFitResult(
        score=matched_demand / total_demand,
    )

def calculate_scenario_definition_fit(
    scenario: ScenarioDefinition,
    capabilities: dict[StrategicDemand, float],
) -> ScenarioFitResult:
    if not isinstance(
        scenario,
        ScenarioDefinition,
    ):
        raise TypeError(
            "scenario must be a ScenarioDefinition."
        )

    return calculate_scenario_fit(
        demands=scenario.strategic_demands,
        capabilities=capabilities,
    )

def calculate_scenario_fit_from_profile(
    demands: tuple[ScenarioDemand, ...],
    capability_profile: ScenarioCapabilityProfile,
) -> ScenarioFitResult:
    if not isinstance(
        capability_profile,
        ScenarioCapabilityProfile,
    ):
        raise TypeError(
            "capability_profile must be a ScenarioCapabilityProfile."
        )

    return calculate_scenario_fit(
        demands=demands,
        capabilities=capability_profile.to_mapping(),
    )