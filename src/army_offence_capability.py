from army import Army
from combat_benchmark import (
    CombatBenchmark,
    DEFAULT_COMBAT_BENCHMARK,
)
from profile_offensive_combat_score import (
    calculate_profile_offensive_combat_score,
)


def calculate_army_offensive_combat_score(
    army: Army,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    charge_probability: float = 1.0,
) -> float:
    total_models = army.model_count()

    if total_models == 0:
        return 0.0

    total_score = 0.0

    for entry in army.entries:

        if not entry.counts_as_model:
            continue

        profile_score = (
            calculate_profile_offensive_combat_score(
                entry.configured_profile,
                benchmark,
                charge_probability=charge_probability,
            )
        )

        total_score += (
            profile_score
            * entry.quantity
        )

    return total_score / total_models

def calculate_army_offensive_output_density(
    army: Army,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    charge_probability: float = 1.0,
) -> float:
    army_points = army.total_points()

    if army_points <= 0:
        return 0.0

    total_score = 0.0

    for entry in army.entries:

        if not entry.counts_as_model:
            continue

        score = calculate_profile_offensive_combat_score(
            entry.configured_profile,
            benchmark,
            charge_probability=charge_probability,
        )

        total_score += (
            score
            * entry.quantity
        )

    return (
        total_score
        * 100
        / army_points
    )