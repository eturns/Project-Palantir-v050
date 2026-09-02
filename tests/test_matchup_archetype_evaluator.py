from matchup_archetype import MatchupArchetype
from matchup_archetype_evaluator import (
    calculate_matchup_archetype_score,
)
from matchup_result import MatchupResult


def test_calculates_mean_matchup_score_for_archetype():
    archetype = MatchupArchetype(
        id="TEST_ARCHETYPE",
        name="Test Archetype",
        profile_ids=(
            "A",
            "B",
        ),
    )

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
        MatchupResult(
            target_profile_id="C",
            target_profile_name="Target C",
            score=0.90,
        ),
    )

    score = calculate_matchup_archetype_score(
        archetype=archetype,
        results=results,
    )

    assert score == 0.50

def test_archetype_with_no_matching_results_has_zero_score():
    archetype = MatchupArchetype(
        id="NO_MATCH",
        name="No Match",
        profile_ids=(
            "MISSING",
        ),
    )

    results = (
        MatchupResult(
            target_profile_id="A",
            target_profile_name="Target A",
            score=0.40,
        ),
    )

    score = calculate_matchup_archetype_score(
        archetype=archetype,
        results=results,
    )

    assert score == 0.0