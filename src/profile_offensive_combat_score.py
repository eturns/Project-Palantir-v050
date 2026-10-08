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
from configured_profile import ConfiguredProfile
from configured_duel_probability import (
    calculate_configured_duel_probability,
)
from configured_wound_probability import (
    calculate_configured_wound_probability,
)
from charge_opportunity import (
    calculate_charge_weighted_duel_probability,
)
from special_rule_strike_damage import (
    get_special_rule_strike_damage,
)
from special_rule_post_prevention_effect import (
    get_special_rule_post_prevention_effect,
)
from post_prevention_effect import (
    PostPreventionEffect,
)
from wound_context import (
    WoundContext,
)
from wound_attack_type import (
    WoundAttackType,
)

def calculate_profile_offensive_combat_score(
    profile: Profile | ConfiguredProfile,
    benchmark: CombatBenchmark,
    *,
    charge_probability: float = 1.0,
) -> float:

    post_prevention_effect = PostPreventionEffect.NONE

    if isinstance(
        profile,
        ConfiguredProfile,
    ):
        benchmark_profile = Profile(
            id="OFFENCE_BENCHMARK",
            name="Offence Benchmark",
            points=0,
            movement=6,
            fight=benchmark.fight,
            shooting="4+",
            strength=benchmark.strength,
            defence=benchmark.defence,
            attacks=benchmark.attacks,
            wounds=benchmark.wounds,
            courage="4+",
            intelligence="4+",
            might=0,
            will=0,
            fate=0,
            max_in_army=0,
        )

        defender = ConfiguredProfile(
            profile=benchmark_profile,
        )

        duel_result = (
            calculate_charge_weighted_duel_probability(
                attacker=profile,
                defender=defender,
                charge_probability=charge_probability,
            )
        )

        wound_probability = (
            calculate_configured_wound_probability(
                attacker=profile,
                defender=defender,
            )
        )

        strike_damage = get_special_rule_strike_damage(
            attacker=profile,
            defender=defender,
        )

        post_prevention_effect = (
            get_special_rule_post_prevention_effect(
                attacker=profile,
                context=WoundContext(
                    attack_type=WoundAttackType.STRIKE,
                ),
            )
        )

        wounds_per_successful_strike = (
            strike_damage.wounds_per_successful_strike
        )

        attacks = profile.effective_attacks

    else:
        attacks = profile.attacks
        wounds_per_successful_strike = 1

        duel_result = calculate_basic_duel_probability(
            attacker_attacks=attacks,
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
        number_of_strikes=attacks,
        wound_probability=wound_probability,
    )

    if (
        isinstance(profile, ConfiguredProfile)
        and post_prevention_effect
        is PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO
    ):
        successful_strikes_required = 1
    else:
        successful_strikes_required = (
            benchmark.wounds
            + wounds_per_successful_strike
            - 1
        ) // wounds_per_successful_strike

    probability_of_defeating_benchmark = sum(
        wound_distribution[
            successful_strikes_required:
        ],
        Fraction(0, 1),
    )

    return (
        duel_result.attacker_win_probability
        * float(
            probability_of_defeating_benchmark,
        )
    )