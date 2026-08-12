from fractions import Fraction

from combat_benchmark import CombatBenchmark
from duel_probability import (
    calculate_basic_duel_probability,
)
from profiles import Profile
from wound_probability import (
    get_wound_distribution,
    get_wound_probability,
)
from wound_table import get_wound_target


def calculate_profile_offensive_combat_score(
    profile: Profile,
    benchmark: CombatBenchmark,
) -> float:
    duel_result = calculate_basic_duel_probability(
        attacker_attacks=profile.attacks,
        attacker_fight=profile.fight,
        defender_attacks=benchmark.attacks,
        defender_fight=benchmark.fight,
    )

    wound_target = get_wound_target(
        strength=profile.strength,
        defence=benchmark.defence,
    )

    wound_probability = get_wound_probability(
        wound_target,
    )

    wound_distribution = get_wound_distribution(
        number_of_strikes=profile.attacks,
        wound_probability=wound_probability,
    )

    probability_of_defeating_benchmark = sum(
        wound_distribution[
            benchmark.wounds:
        ],
        Fraction(0, 1),
    )

    return (
        duel_result.attacker_win_probability
        * float(
            probability_of_defeating_benchmark,
        )
    )