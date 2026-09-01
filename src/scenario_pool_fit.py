from dataclasses import dataclass
from scenario_definition import (
    ScenarioDefinition,
    ScenarioPool,
)
from scenario_capability import ScenarioCapabilityProfile
from scenario_demand import StrategicDemand
from scenario_fit import (
    ScenarioFitResult,
    calculate_scenario_definition_fit,
)
from scenario_catalogue import (
    get_official_scenarios_by_pool,
)

def calculate_scenario_pool_fit(
    scenario_fits: tuple[ScenarioFitResult, ...],
) -> float:
    if not scenario_fits:
        raise ValueError(
            "scenario_fits cannot be empty."
        )

    if not all(
        isinstance(
            scenario_fit,
            ScenarioFitResult,
        )
        for scenario_fit in scenario_fits
    ):
        raise TypeError(
            "scenario_fits must contain only ScenarioFitResult values."
        )

    return sum(
        scenario_fit.score
        for scenario_fit in scenario_fits
    ) / len(scenario_fits)

@dataclass(frozen=True)
class ScenarioPoolFitResult:
    pool: ScenarioPool
    score: float

    def __post_init__(self) -> None:
        if not isinstance(
            self.pool,
            ScenarioPool,
        ):
            raise TypeError(
                "pool must be a ScenarioPool."
            )

        if not 0.0 <= self.score <= 1.0:
            raise ValueError(
                "Scenario pool fit score must be between 0.0 and 1.0."
            )

@dataclass(frozen=True)
class ScenarioPoolFitSummary:
    pool_results: tuple[ScenarioPoolFitResult, ...]
    strongest: ScenarioPoolFitResult
    weakest: ScenarioPoolFitResult

def calculate_scenario_pool_fit_from_definitions(
    scenarios: tuple[ScenarioDefinition, ...],
    capabilities: dict[StrategicDemand, float],
) -> float:
    if scenarios:
        pool = scenarios[0].pool

        if any(
            scenario.pool is not pool
            for scenario in scenarios
        ):
            raise ValueError(
                "scenarios must all belong to the same pool."
            )

    scenario_fits = tuple(
        calculate_scenario_definition_fit(
            scenario=scenario,
            capabilities=capabilities,
        )
        for scenario in scenarios
    )

    return calculate_scenario_pool_fit(
        scenario_fits=scenario_fits,
    )

def calculate_official_scenario_pool_fit(
    pool: ScenarioPool,
    capabilities: dict[StrategicDemand, float],
) -> float:
    scenarios = get_official_scenarios_by_pool(
        pool=pool,
    )

    return calculate_scenario_pool_fit_from_definitions(
        scenarios=scenarios,
        capabilities=capabilities,
    )

def calculate_all_official_scenario_pool_fits(
    capabilities: dict[StrategicDemand, float],
) -> dict[ScenarioPool, float]:
    return {
        pool: calculate_official_scenario_pool_fit(
            pool=pool,
            capabilities=capabilities,
        )
        for pool in ScenarioPool
    }

def build_official_scenario_pool_fit_report(
    capabilities: dict[StrategicDemand, float],
) -> tuple[ScenarioPoolFitResult, ...]:
    pool_fits = calculate_all_official_scenario_pool_fits(
        capabilities=capabilities,
    )

    return tuple(
        ScenarioPoolFitResult(
            pool=pool,
            score=score,
        )
        for pool, score in pool_fits.items()
    )

def build_official_scenario_pool_fit_report_from_profile(
    capability_profile: ScenarioCapabilityProfile,
) -> tuple[ScenarioPoolFitResult, ...]:
    return build_official_scenario_pool_fit_report(
        capabilities=capability_profile.to_mapping(),
    )

def get_strongest_scenario_pool(
    pool_results: tuple[ScenarioPoolFitResult, ...],
) -> ScenarioPoolFitResult:
    return max(
        pool_results,
        key=lambda result: result.score,
    )


def get_weakest_scenario_pool(
    pool_results: tuple[ScenarioPoolFitResult, ...],
) -> ScenarioPoolFitResult:
    return min(
        pool_results,
        key=lambda result: result.score,
    )

def get_strongest_scenario_pool(
    pool_results: tuple[ScenarioPoolFitResult, ...],
) -> ScenarioPoolFitResult:
    if not pool_results:
        raise ValueError(
            "pool_results cannot be empty."
        )

    return max(
        pool_results,
        key=lambda result: result.score,
    )


def get_weakest_scenario_pool(
    pool_results: tuple[ScenarioPoolFitResult, ...],
) -> ScenarioPoolFitResult:
    if not pool_results:
        raise ValueError(
            "pool_results cannot be empty."
        )

    return min(
        pool_results,
        key=lambda result: result.score,
    )

def build_official_scenario_pool_fit_summary(
    capabilities: dict[StrategicDemand, float],
) -> ScenarioPoolFitSummary:
    pool_results = build_official_scenario_pool_fit_report(
        capabilities=capabilities,
    )

    return ScenarioPoolFitSummary(
        pool_results=pool_results,
        strongest=get_strongest_scenario_pool(
            pool_results=pool_results,
        ),
        weakest=get_weakest_scenario_pool(
            pool_results=pool_results,
        ),
    )

def build_official_scenario_pool_fit_summary_from_profile(
    capability_profile: ScenarioCapabilityProfile,
) -> ScenarioPoolFitSummary:
    return build_official_scenario_pool_fit_summary(
        capabilities=capability_profile.to_mapping(),
    )