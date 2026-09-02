from dataclasses import dataclass

from matchup_result import MatchupResult


@dataclass(frozen=True)
class MatchupPortfolioSummary:
    results: tuple[MatchupResult, ...]
    mean_score: float


def build_matchup_portfolio_summary(
    *,
    results: tuple[MatchupResult, ...],
) -> MatchupPortfolioSummary:
    if not results:
        return MatchupPortfolioSummary(
            results=(),
            mean_score=0.0,
        )

    mean_score = (
        sum(
            result.score
            for result in results
        )
        / len(results)
    )

    return MatchupPortfolioSummary(
        results=results,
        mean_score=mean_score,
    )