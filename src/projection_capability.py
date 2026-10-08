from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)
from battlefield_effects_score import (
    calculate_battlefield_effects_score,
)
from army import Army
from army_list import ArmyList
from battlefield_effects_input_builder import (
    build_battlefield_effects_inputs,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand
from army_metric_densities import (
    calculate_army_metric_densities,
)
from objective_normalisation import (
    MAGIC_DENSITY_MAX,
    normalise_battlefield_effect,
)
from army_shooting_capability import (
    calculate_army_shooting_output_density,
)
from configured_profile import ConfiguredProfile
from profiles import Profile

def build_shooting_benchmark_defender() -> ConfiguredProfile:
    return ConfiguredProfile(
        profile=Profile(
            id="SHOOTING_BENCHMARK",
            name="Shooting Benchmark",
            points=0,
            movement=6,
            fight=4,
            shooting="4+",
            strength=4,
            defence=6,
            attacks=1,
            wounds=1,
            courage="6+",
            intelligence="6+",
            might=0,
            will=0,
            fate=0,
            max_in_army=0,
        )
    )

def calculate_projection_capability(
    battlefield_effects_score: int | float,
) -> ScenarioCapability:
    if (
        not isinstance(
            battlefield_effects_score,
            (int, float),
        )
        or isinstance(
            battlefield_effects_score,
            bool,
        )
    ):
        raise TypeError(
            "battlefield_effects_score must be int or float."
        )

    if not 0.0 <= battlefield_effects_score <= 1.0:
        raise ValueError(
            "battlefield_effects_score must be between 0.0 and 1.0."
        )

    return ScenarioCapability(
        dimension=StrategicDemand.PROJECTION,
        value=battlefield_effects_score,
    )


def calculate_projection_capability_from_inputs(
    inputs: BattlefieldEffectsInputs,
) -> ScenarioCapability:
    if not isinstance(
        inputs,
        BattlefieldEffectsInputs,
    ):
        raise TypeError(
            "inputs must be a BattlefieldEffectsInputs."
        )

    battlefield_effects_score = (
        calculate_battlefield_effects_score(
            inputs,
        )
    )

    return calculate_projection_capability(
        battlefield_effects_score=(
            battlefield_effects_score
        ),
    )

def calculate_projection_capability_from_army(
    army: Army,
    army_list: ArmyList,
    *,
    shooting_density: float | None = None,
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

    if shooting_density is None:
        shooting_density = (
            calculate_army_shooting_output_density(
                army=army,
                defender=build_shooting_benchmark_defender(),
            )
        )

    inputs = build_battlefield_effects_inputs(
        army,
        army_list,
        shooting_density=shooting_density,
    )

    densities = calculate_army_metric_densities(
        army,
        army_list,
    )

    magic = normalise_battlefield_effect(
        densities.magic,
        MAGIC_DENSITY_MAX,
    )

    projection_score = (
        magic
        + inputs.shooting
    ) / 2

    return calculate_projection_capability(
        battlefield_effects_score=(
            projection_score
        ),
    )
