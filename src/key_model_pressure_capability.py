from army import Army
from army_list import ArmyList
from battlefield_effects_input_builder import (
    build_battlefield_effects_inputs,
)
from combat_benchmark import CombatBenchmark
from attrition_output_capability import (
    calculate_attrition_output_capability_from_army,
)

from scenario_capability import (
    ScenarioCapability,
)
from scenario_demand import (
    StrategicDemand,
)


def calculate_key_model_pressure_capability(
    attrition_output: int | float,
    hero_hunting: int | float,
) -> ScenarioCapability:
    inputs = (
        attrition_output,
        hero_hunting,
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
        attrition_output
        + hero_hunting
    ) / 2

    return ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESSURE,
        value=value,
    )

def calculate_key_model_pressure_from_army(
    army: Army,
    army_list: ArmyList,
    combat_benchmark: CombatBenchmark,
    benchmark_combat_capability: int | float,
) -> ScenarioCapability:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    if not isinstance(
        army_list,
        ArmyList,
    ):
        raise TypeError(
            "army_list must be an ArmyList."
        )

    if not isinstance(
        combat_benchmark,
        CombatBenchmark,
    ):
        raise TypeError(
            "combat_benchmark must be a CombatBenchmark."
        )

    attrition_output = (
        calculate_attrition_output_capability_from_army(
            army=army,
            combat_benchmark=combat_benchmark,
            benchmark_combat_capability=(
                benchmark_combat_capability
            ),
        )
    )

    battlefield_effects = (
        build_battlefield_effects_inputs(
            army=army,
            army_list=army_list,
        )
    )

    return calculate_key_model_pressure_capability(
        attrition_output=attrition_output.value,
        hero_hunting=battlefield_effects.hero_hunting,
    )