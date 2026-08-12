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


def calculate_profile_combat_capability(
    profile: Profile,
    benchmark: CombatBenchmark,
) -> float:
    offensive_score = (
        calculate_profile_offensive_combat_score(
            profile,
            benchmark,
        )
    )

    defensive_score = (
        calculate_profile_defensive_combat_score(
            profile,
            benchmark,
        )
    )

    return (
        offensive_score * OFFENSIVE_COMBAT_WEIGHT
        + defensive_score * DEFENSIVE_COMBAT_WEIGHT
    )