from combat_benchmark import CombatBenchmark
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from profiles import Profile
from wound_capacity import (
    calculate_wound_capacity,
)
from army import Army

def calculate_staying_power(
    defensive_combat: int | float,
    wound_capacity: int | float,
) -> float:
    inputs = (
        defensive_combat,
        wound_capacity,
    )

    if any(
        (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        )
        for value in inputs
    ):
        raise TypeError(
            "staying power inputs must be int or float."
        )

    if any(
        not 0.0 <= value <= 1.0
        for value in inputs
    ):
        raise ValueError(
            "staying power inputs must be between 0.0 and 1.0."
        )

    return (
        defensive_combat
        + wound_capacity
    ) / 2

def calculate_staying_power_from_profile(
    profile: Profile,
    benchmark: CombatBenchmark,
) -> float:
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

    defensive_combat = (
        calculate_profile_defensive_combat_score(
            profile=profile,
            benchmark=benchmark,
        )
    )

    wound_capacity = calculate_wound_capacity(
        wounds=profile.wounds,
    )

    return calculate_staying_power(
        defensive_combat=defensive_combat,
        wound_capacity=wound_capacity,
    )

def calculate_army_staying_power(
    army: Army,
    benchmark: CombatBenchmark,
) -> float:
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

    total_models = army.model_count()

    if total_models == 0:
        return 0.0

    weighted_total = 0.0

    for entry in army.entries:
        profile_staying_power = (
            calculate_staying_power_from_profile(
                profile=entry.profile,
                benchmark=benchmark,
            )
        )

        weighted_total += (
            profile_staying_power
            * entry.quantity
        )

    return weighted_total / total_models