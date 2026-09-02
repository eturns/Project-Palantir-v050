from matchup_portfolio_summary import (
    MatchupPortfolioSummary,
     build_matchup_portfolio_summary,
)
from matchup_result import MatchupResult


def test_matchup_portfolio_summary_stores_results_and_mean_score():
    results = (
        MatchupResult(
            target_profile_id="A",
            target_profile_name="Target A",
            score=0.40,
        ),
        MatchupResult(
            target_profile_id="B",
            target_profile_name="Target B",
            score=0.60,
        ),
    )

    summary = MatchupPortfolioSummary(
        results=results,
        mean_score=0.50,
    )

    assert summary.results == results
    assert summary.mean_score == 0.50

def test_builds_matchup_portfolio_summary_from_results():
    results = (
        MatchupResult(
            target_profile_id="A",
            target_profile_name="Target A",
            score=0.40,
        ),
        MatchupResult(
            target_profile_id="B",
            target_profile_name="Target B",
            score=0.60,
        ),
    )

    summary = build_matchup_portfolio_summary(
        results=results,
    )

    assert summary.results == results
    assert summary.mean_score == 0.50

def test_empty_matchup_portfolio_summary_has_zero_mean_score():
    summary = build_matchup_portfolio_summary(
        results=(),
    )

    assert summary.results == ()
    assert summary.mean_score == 0.0