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
    calculate_deployment_recovery_from_army,
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


def build_scenario_capability_profile(
    army: Army,
    army_list: ArmyList,
    key_profile: Profile,
    combat_benchmark: CombatBenchmark,
    benchmark_presence: int | float,
    benchmark_manoeuvrability: int | float,
    benchmark_combat_capability: int | float,
    benchmark_fate: int | float,
) -> ScenarioCapabilityProfile:
    profiles = tuple(
        entry.profile
        for entry in army.entries
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

    key_model_preservation = (
        calculate_key_model_preservation_from_profile(
            profile=key_profile,
            benchmark=combat_benchmark,
            benchmark_fate=benchmark_fate,
        )
    )

    state_resilience = calculate_state_resilience_from_army(
        army=army,
        benchmark=combat_benchmark,
    )

    deployment_recovery = (
        calculate_deployment_recovery_from_army(
            army=army,
            benchmark=combat_benchmark,
            benchmark_manoeuvrability=(
                benchmark_manoeuvrability
            ),
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