from matchup_result import MatchupResult


def test_matchup_result_stores_target_and_score():
    result = MatchupResult(
        target_profile_id="BENCH_ELROND",
        target_profile_name="Elrond, Master of Rivendell",
        score=0.625,
    )

    assert result.target_profile_id == "BENCH_ELROND"
    assert (
        result.target_profile_name
        == "Elrond, Master of Rivendell"
    )
    assert result.score == 0.625

def test_matchup_result_stores_offensive_and_defensive_scores():
    result = MatchupResult(
        target_profile_id="BENCH_ELROND",
        target_profile_name="Elrond, Master of Rivendell",
        score=0.625,
        offensive_score=0.700,
        defensive_score=0.550,
    )

    assert result.score == 0.625
    assert result.offensive_score == 0.700
    assert result.defensive_score == 0.550