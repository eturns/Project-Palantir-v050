from matchup_evaluator import calculate_matchup_result
from matchup_result import MatchupResult
from optimiser_candidate import OptimiserCandidate
from profiles import Profile


def calculate_matchup_portfolio_results(
    *,
    candidate: OptimiserCandidate,
    target_profiles: list[Profile],
) -> tuple[MatchupResult, ...]:
    return tuple(
        calculate_matchup_result(
            candidate=candidate,
            target_profile=target_profile,
        )
        for target_profile in target_profiles
    )