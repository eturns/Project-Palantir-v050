from army import Army
from army_list import ArmyList
from attrition_output_capability import (
    calculate_attrition_output_capability_from_army,
)
from combat_benchmark import CombatBenchmark
from concentrated_control_capability import (
    calculate_concentrated_control_from_army,
)
from deployment_recovery_capability import (
    calculate_deployment_recovery_capability,
)
from distributed_control_capability import (
    calculate_distributed_control_from_profiles,
)
from key_model_preservation_capability import (
    calculate_key_model_preservation_from_profile,
)
from key_model_pressure_capability import (
    calculate_key_model_pressure_from_army,
)
from mobility_capability import (
    calculate_mobility_capability_from_army,
)
from profiles import Profile
from projection_capability import (
    calculate_projection_capability_from_army,
)
from scenario_capability import (
    ScenarioCapabilityProfile,
)
from state_resilience_capability import (
    calculate_state_resilience_from_army,
)
from resurrection_resilience_calculator import (
    calculate_resurrection_modified_state_resilience,
)
from scenario_context import ScenarioContext
from resurrection_config import ResurrectionConfig

def build_scenario_capability_profile(
    army: Army,
    context: ScenarioContext,
    preservation_profile: Profile | None = None,
    resurrection_config: ResurrectionConfig | None = None,
) -> ScenarioCapabilityProfile:
    army_list = context.army_list
    key_profile = context.key_profile
    combat_benchmark = context.combat_benchmark
    benchmark_presence = context.benchmark_presence
    benchmark_manoeuvrability = (
        context.benchmark_manoeuvrability
    )
    benchmark_combat_capability = (
        context.benchmark_combat_capability
    )
    benchmark_fate = context.benchmark_fate

    profiles = tuple(
        entry.profile
        for entry in army.entries
        if entry.counts_as_model
        for _ in range(entry.quantity)
    )

    distributed_control = (
        calculate_distributed_control_from_profiles(
            profiles=profiles,
            benchmark_presence=benchmark_presence,
        )
    )

    concentrated_control = (
        calculate_concentrated_control_from_army(
            army=army,
            benchmark_presence=benchmark_presence,
            combat_benchmark=combat_benchmark,
            benchmark_combat_capability=(
                benchmark_combat_capability
            ),
        )
    )

    mobility = calculate_mobility_capability_from_army(
        army=army,
        benchmark_manoeuvrability=(
            benchmark_manoeuvrability
        ),
    )

    projection = calculate_projection_capability_from_army(
        army=army,
        army_list=army_list,
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

    key_model_pressure = (
        calculate_key_model_pressure_from_army(
            army=army,
            army_list=army_list,
            combat_benchmark=combat_benchmark,
            benchmark_combat_capability=(
                benchmark_combat_capability
            ),
        )
    )

    if preservation_profile is None:
        preservation_profile = key_profile

    key_model_preservation = (
        calculate_key_model_preservation_from_profile(
            profile=preservation_profile,
            benchmark=combat_benchmark,
            benchmark_fate=benchmark_fate,
            army=army,
            army_list=army_list,
        )
    )

    state_resilience = calculate_state_resilience_from_army(
        army=army,
        benchmark=combat_benchmark,
    )

    if resurrection_config is not None:
        state_resilience = (
            calculate_resurrection_modified_state_resilience(
                state_resilience=state_resilience,
                resurrection_capable_models=(
                    resurrection_config.resurrection_capable_models
                ),
                starting_models=(
                    resurrection_config.starting_models
                ),
                resilience_weight=(
                    resurrection_config.resilience_weight
                ),
                necromancer_remaining_will=(
                    resurrection_config.necromancer_remaining_will
                ),
                distance_inches=(
                    resurrection_config.distance_inches
                ),
                will_points_available_to_spend=(
                    resurrection_config.will_points_available_to_spend
                ),
            )
        )

    deployment_recovery = (
        calculate_deployment_recovery_capability(
            mobility=mobility.value,
            state_resilience=state_resilience.value,
        )
    )

    return ScenarioCapabilityProfile(
        capabilities=(
            distributed_control,
            concentrated_control,
            mobility,
            projection,
            attrition_output,
            key_model_pressure,
            key_model_preservation,
            state_resilience,
            deployment_recovery,
        ),
    )