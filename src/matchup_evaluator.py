from combat_benchmark import CombatBenchmark
from matchup_result import MatchupResult
from optimiser_candidate import OptimiserCandidate
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)
from profile_offensive_combat_score import (
    calculate_profile_offensive_combat_score,
)
from profiles import Profile


def calculate_matchup_result(
    *,
    candidate: OptimiserCandidate,
    target_profile: Profile,
) -> MatchupResult:
    benchmark = CombatBenchmark(
        fight=target_profile.fight,
        strength=target_profile.strength,
        defence=target_profile.defence,
        attacks=target_profile.attacks,
        wounds=target_profile.wounds,
    )

    total_models = candidate.army.model_count()

    if total_models == 0:
        offensive_score = 0.0
        defensive_score = 0.0

    else:
        offensive_score = sum(
            calculate_profile_offensive_combat_score(
                entry.profile,
                benchmark,
            )
            * entry.quantity
            for entry in candidate.army.entries
        ) / total_models

        defensive_score = sum(
            calculate_profile_defensive_combat_score(
                entry.profile,
                benchmark,
            )
            * entry.quantity
            for entry in candidate.army.entries
        ) / total_models

    score = (
        offensive_score * 0.5
        + defensive_score * 0.5
    )

    return MatchupResult(
        target_profile_id=target_profile.id,
        target_profile_name=target_profile.name,
        score=score,
        offensive_score=offensive_score,
        defensive_score=defensive_score,
    )