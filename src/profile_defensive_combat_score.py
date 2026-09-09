from combat_benchmark import CombatBenchmark
from duel_probability import (
    calculate_basic_duel_probability,
)
from profiles import Profile
from wound_probability import (
    get_wound_probability,
)
from wound_table import get_wound_target
from configured_profile import ConfiguredProfile

def calculate_profile_defensive_combat_score(
    profile: Profile | ConfiguredProfile,
    benchmark: CombatBenchmark,
) -> float:
    if isinstance(
        profile,
        ConfiguredProfile,
    ):
        base_profile = profile.profile
        defence = profile.effective_defence
    else:
        base_profile = profile
        defence = profile.defence

    duel_result = calculate_basic_duel_probability(
        attacker_attacks=benchmark.attacks,
        attacker_fight=benchmark.fight,
        defender_attacks=base_profile.attacks,
        defender_fight=base_profile.fight,
    )

    wound_target = get_wound_target(
        strength=benchmark.strength,
        defence=defence,
    )

    wound_probability = float(
        get_wound_probability(
            wound_target,
        )
    )

    expected_incoming_wounds = (
        duel_result.attacker_win_probability
        * benchmark.attacks
        * wound_probability
    )

    return max(
        0.0,
        1.0 - expected_incoming_wounds,
    )