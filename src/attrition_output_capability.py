from army import Army
from army_combat_capability import (
    calculate_army_combat_capability,
)
from combat_benchmark import CombatBenchmark
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def calculate_attrition_output_capability(
    combat_capability: int | float,
    benchmark_combat_capability: int | float,
) -> ScenarioCapability:
    if (
        not isinstance(combat_capability, (int, float))
        or isinstance(combat_capability, bool)
    ):
        raise TypeError(
            "combat_capability must be int or float."
        )

    if (
        not isinstance(
            benchmark_combat_capability,
            (int, float),
        )
        or isinstance(
            benchmark_combat_capability,
            bool,
        )
    ):
        raise TypeError(
            "benchmark_combat_capability must be int or float."
        )

    if combat_capability < 0:
        raise ValueError(
            "combat_capability cannot be negative."
        )

    if benchmark_combat_capability <= 0:
        raise ValueError(
            "benchmark_combat_capability must be greater than zero."
        )

    value = (
        combat_capability
        / (
            combat_capability
            + benchmark_combat_capability
        )
    )

    return ScenarioCapability(
        dimension=StrategicDemand.ATTRITION_OUTPUT,
        value=value,
    )


def calculate_attrition_output_capability_from_army(
    army: Army,
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

    combat_capability = calculate_army_combat_capability(
        army=army,
        benchmark=combat_benchmark,
    )

    return calculate_attrition_output_capability(
        combat_capability=combat_capability,
        benchmark_combat_capability=(
            benchmark_combat_capability
        ),
    )