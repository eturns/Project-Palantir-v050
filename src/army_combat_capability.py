from army import Army
from combat_benchmark import CombatBenchmark
from profile_combat_capability import (
    calculate_profile_combat_capability,
)


def calculate_army_combat_capability(
    army: Army,
    benchmark: CombatBenchmark,
) -> float:
    total_models = army.model_count()

    if total_models == 0:
        return 0.0

    weighted_score = 0.0

    for entry in army.entries:
        profile_score = (
            calculate_profile_combat_capability(
                entry.profile,
                benchmark,
            )
        )

        weighted_score += (
            profile_score
            * entry.quantity
        )

    return weighted_score / total_models