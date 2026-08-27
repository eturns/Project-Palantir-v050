from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand
from army import Army
from combat_benchmark import CombatBenchmark
from resource_capacity_score import (
    calculate_resource_capacity_score,
)
from staying_power_capability import (
    calculate_army_staying_power,
)

def calculate_state_resilience_capability(
    model_state_capacity: int | float,
    resource_capacity: int | float,
) -> ScenarioCapability:
    inputs = (
        model_state_capacity,
        resource_capacity,
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
        model_state_capacity
        + resource_capacity
    ) / 2

    return ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=value,
    )

def calculate_state_resilience_from_army(
    army: Army,
    benchmark: CombatBenchmark,
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

    staying_power = calculate_army_staying_power(
        army=army,
        benchmark=benchmark,
    )

    resource_capacity = calculate_resource_capacity_score(
        might=army.total_might(),
        will=army.total_will(),
        fate=army.total_fate(),
        army_points=army.total_points(),
    )

    return calculate_state_resilience_capability(
        model_state_capacity=staying_power,
        resource_capacity=resource_capacity,
    )