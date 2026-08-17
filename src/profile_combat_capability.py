from functools import lru_cache

from combat_benchmark import CombatBenchmark
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from profile_offensive_combat_score import (
    calculate_profile_offensive_combat_score,
)
from profiles import Profile


OFFENSIVE_COMBAT_WEIGHT = 0.5
DEFENSIVE_COMBAT_WEIGHT = 0.5


@lru_cache(maxsize=None)
def _calculate_profile_combat_capability_cached(
    *,
    profile_fight: int,
    profile_strength: int,
    profile_defence: int,
    profile_attacks: int,
    profile_wounds: int,
    benchmark_fight: int,
    benchmark_strength: int,
    benchmark_defence: int,
    benchmark_attacks: int,
    benchmark_wounds: int,
    offensive_calculator,
    defensive_calculator,
) -> float:
    class CombatProfileView:
        fight = profile_fight
        strength = profile_strength
        defence = profile_defence
        attacks = profile_attacks
        wounds = profile_wounds

    benchmark = CombatBenchmark(
        fight=benchmark_fight,
        strength=benchmark_strength,
        defence=benchmark_defence,
        attacks=benchmark_attacks,
        wounds=benchmark_wounds,
    )

    offensive_score = offensive_calculator(
        CombatProfileView,
        benchmark,
    )

    defensive_score = defensive_calculator(
        CombatProfileView,
        benchmark,
    )

    return (
        offensive_score * OFFENSIVE_COMBAT_WEIGHT
        + defensive_score * DEFENSIVE_COMBAT_WEIGHT
    )


def calculate_profile_combat_capability(
    profile: Profile,
    benchmark: CombatBenchmark,
) -> float:
    return _calculate_profile_combat_capability_cached(
        profile_fight=profile.fight,
        profile_strength=profile.strength,
        profile_defence=profile.defence,
        profile_attacks=profile.attacks,
        profile_wounds=profile.wounds,
        benchmark_fight=benchmark.fight,
        benchmark_strength=benchmark.strength,
        benchmark_defence=benchmark.defence,
        benchmark_attacks=benchmark.attacks,
        benchmark_wounds=benchmark.wounds,
        offensive_calculator=(
            calculate_profile_offensive_combat_score
        ),
        defensive_calculator=(
            calculate_profile_defensive_combat_score
        ),
    )