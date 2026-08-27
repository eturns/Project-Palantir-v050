from scenario_capability import (
    ScenarioCapability,
)
from scenario_demand import (
    StrategicDemand,
)
from army import Army
from combat_benchmark import CombatBenchmark
from mobility_capability import (
    calculate_mobility_capability_from_army,
)
from state_resilience_capability import (
    calculate_state_resilience_from_army,
)

def calculate_deployment_recovery_capability(
    mobility: int | float,
    state_resilience: int | float,
) -> ScenarioCapability:
    inputs = (
        mobility,
        state_resilience,
    )

    if any(
        (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        )
        for value in inputs
    ):
        raise TypeError(
            "capability inputs must be int or float."
        )

    if any(
        not 0.0 <= value <= 1.0
        for value in inputs
    ):
        raise ValueError(
            "capability inputs must be between 0.0 and 1.0."
        )

    value = (
        mobility
        + state_resilience
    ) / 2

    return ScenarioCapability(
        dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
        value=value,
    )

def calculate_deployment_recovery_from_army(
    army: Army,
    benchmark: CombatBenchmark,
    benchmark_manoeuvrability: int | float,
) -> ScenarioCapability:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    if not isinstance(
        benchmark,
        CombatBenchmark,
    ):
        raise TypeError(
            "benchmark must be a CombatBenchmark."
        )

    mobility = calculate_mobility_capability_from_army(
        army=army,
        benchmark_manoeuvrability=benchmark_manoeuvrability,
    )

    state_resilience = calculate_state_resilience_from_army(
        army=army,
        benchmark=benchmark,
    )

    return calculate_deployment_recovery_capability(
        mobility=mobility.value,
        state_resilience=state_resilience.value,
    )