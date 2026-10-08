"""Generic combined combat capability.

DEV-077S-I2-C-H3-C:
Preserve the cached statline-based combat calculation
while supplying Fate and Will required by Defence v2.

This adapter represents effective combat characteristics.
It does not carry equipment-specific or special-rule
mechanics; those require configured-profile evaluation.
"""

from functools import lru_cache

from combat_benchmark import CombatBenchmark
from configured_profile import ConfiguredProfile
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
    profile_fate: int,
    profile_will: int,
    benchmark_fight: int,
    benchmark_strength: int,
    benchmark_defence: int,
    benchmark_attacks: int,
    benchmark_wounds: int,
    offensive_calculator,
    defensive_calculator,
) -> float:
    """Evaluate a cached effective statline."""

    class CombatProfileView:
        fight = profile_fight
        strength = profile_strength
        defence = profile_defence
        attacks = profile_attacks
        wounds = profile_wounds
        fate = profile_fate
        will = profile_will

        # A statline adapter is not a configured model.
        # No special-rule benefits are inferred.
        special_rules = ()

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
    profile: Profile | ConfiguredProfile,
    benchmark: CombatBenchmark,
) -> float:
    """Calculate combined combat capability from effective stats.

    Configuration-derived numeric statistics are retained.
    The cached legacy route does not resolve contextual
    special rules or equipment effects.
    """

    if isinstance(profile, ConfiguredProfile):
        base_profile = profile.profile

        fight = profile.effective_fight
        strength = profile.effective_strength
        defence = profile.effective_defence
        attacks = profile.effective_attacks
        will = profile.effective_will
    else:
        base_profile = profile

        fight = profile.fight
        strength = profile.strength
        defence = profile.defence
        attacks = profile.attacks
        will = profile.will

    return _calculate_profile_combat_capability_cached(
        profile_fight=fight,
        profile_strength=strength,
        profile_defence=defence,
        profile_attacks=attacks,
        profile_wounds=base_profile.wounds,
        profile_fate=base_profile.fate,
        profile_will=will,
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