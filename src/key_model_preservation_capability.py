from scenario_capability import (
    ScenarioCapability,
)
from scenario_demand import (
    StrategicDemand,
)
from combat_benchmark import CombatBenchmark
from profiles import Profile
from staying_power_capability import (
    calculate_staying_power_from_profile,
)
from army import Army
from owned_army_resource_initialization import (
    get_initial_owned_hero_resource_states,
)
from owned_resource_conversion_initialization import (
    get_initial_owned_resource_conversions,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from battle_length_assumption import BattleHorizon
from resource_strategy import ResourceStrategy
from resource_strategy_budget import calculate_resource_budget
from army_list import ArmyList

def calculate_key_model_preservation_capability(
    defensive_survivability: int | float,
    protective_resources: int | float,
) -> ScenarioCapability:
    inputs = (
        defensive_survivability,
        protective_resources,
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
        defensive_survivability
        + protective_resources
    ) / 2

    return ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
        value=value,
    )

def calculate_protective_resources_from_army_profile(
    army: Army,
    profile: Profile,
    benchmark_fate: int | float,
    army_list: ArmyList | None = None,
) -> float:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    if (
        not isinstance(benchmark_fate, (int, float))
        or isinstance(benchmark_fate, bool)
    ):
        raise TypeError(
            "benchmark_fate must be int or float."
        )

    if benchmark_fate <= 0:
        raise ValueError(
            "benchmark_fate must be greater than zero."
        )

    owned_states = (
        get_initial_owned_hero_resource_states(
            army,
        )
    )

    matching_state = next(
        (
            state
            for state in owned_states
            if state.owner.profile_id == profile.id
        ),
        None,
    )

    if matching_state is None:
        raise ValueError(
            "profile must belong to army."
        )

    owned_conversions = (
        get_initial_owned_resource_conversions(
            army,
        )
    )

    can_convert_will_to_fate = any(
        (
            conversion.owner
            == matching_state.owner
            and (
                conversion.conversion.source_resource_type
                == ResourceType.WILL
            )
            and (
                conversion.conversion.target_resource_use
                == ResourceUse.TAKE_FATE
            )
        )
        for conversion in owned_conversions
    )

    protective_resource_points = (
        matching_state.resources.remaining_fate
    )

    if (
        can_convert_will_to_fate
        and matching_state.resources.remaining_will > 0
    ):
        convertible_will_budget = calculate_resource_budget(
            remaining_resource=(
                matching_state.resources.remaining_will
            ),
            turns_remaining=BattleHorizon.MEDIUM.value,
            strategy=ResourceStrategy.BALANCED,
        )

        defensive_share = 1.0

        if army_list is not None:
            army_rule_ids = {
                army_rule.id
                for army_rule in army_list.army_rules
            }

            if (
                "DG_POWER_OF_THE_NECROMANCER"
                in army_rule_ids
            ):
                defensive_share = 1 / 3

        protective_resource_points += (
            convertible_will_budget
            * defensive_share
        )

    return min(
        protective_resource_points / benchmark_fate,
        1.0,
    )

def calculate_key_model_preservation_from_profile(
    profile: Profile,
    benchmark: CombatBenchmark,
    benchmark_fate: int | float,
    army: Army | None = None,
    army_list: ArmyList | None = None,
) -> ScenarioCapability:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    if not isinstance(
        benchmark,
        CombatBenchmark,
    ):
        raise TypeError(
            "benchmark must be a CombatBenchmark."
        )

    if (
        not isinstance(benchmark_fate, (int, float))
        or isinstance(benchmark_fate, bool)
    ):
        raise TypeError(
            "benchmark_fate must be int or float."
        )

    if benchmark_fate <= 0:
        raise ValueError(
            "benchmark_fate must be greater than zero."
        )

    defensive_survivability = (
        calculate_staying_power_from_profile(
            profile=profile,
            benchmark=benchmark,
        )
    )

    if army is None:
        protective_resources = min(
            profile.fate / benchmark_fate,
            1.0,
        )
    else:
        protective_resources = (
            calculate_protective_resources_from_army_profile(
                army=army,
                profile=profile,
                benchmark_fate=benchmark_fate,
                army_list=army_list,
            )
        )

    return calculate_key_model_preservation_capability(
        defensive_survivability=defensive_survivability,
        protective_resources=protective_resources,
    )