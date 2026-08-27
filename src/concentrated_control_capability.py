from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand
from army import Army
from attrition_output_capability import (
    calculate_attrition_output_capability_from_army,
)
from combat_benchmark import CombatBenchmark
from distributed_control_capability import (
    calculate_distributed_control_capability,
)
from scenario_presence import (
    calculate_army_scenario_presence,
)


def calculate_concentrated_control_capability(
    presence_strength: int | float,
    attrition_output: int | float,
) -> ScenarioCapability:
    inputs = (
        presence_strength,
        attrition_output,
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
        presence_strength
        + attrition_output
    ) / 2

    return ScenarioCapability(
        dimension=StrategicDemand.CONCENTRATED_CONTROL,
        value=value,
    )

def calculate_concentrated_control_from_army(
    army: Army,
    benchmark_presence: int | float,
    combat_benchmark: CombatBenchmark,
    benchmark_combat_capability: int | float,
) -> ScenarioCapability:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    if not isinstance(
        combat_benchmark,
        CombatBenchmark,
    ):
        raise TypeError(
            "combat_benchmark must be a CombatBenchmark."
        )

    profiles = tuple(
        entry.profile
        for entry in army.entries
        for _ in range(entry.quantity)
    )

    scenario_presence = calculate_army_scenario_presence(
        profiles,
    )

    presence_capability = (
        calculate_distributed_control_capability(
            scenario_presence=scenario_presence,
            benchmark_presence=benchmark_presence,
        )
    )

    attrition_capability = (
        calculate_attrition_output_capability_from_army(
            army=army,
            combat_benchmark=combat_benchmark,
            benchmark_combat_capability=(
                benchmark_combat_capability
            ),
        )
    )

    return calculate_concentrated_control_capability(
        presence_strength=presence_capability.value,
        attrition_output=attrition_capability.value,
    )