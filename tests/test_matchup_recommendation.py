from matchup_recommendation import (
    MatchupRecommendation,
    build_matchup_recommendation,
)


def test_matchup_recommendation_stores_strongest_and_weakest_archetypes():
    recommendation = MatchupRecommendation(
        strongest_archetype_id="BASIC_INFANTRY",
        strongest_archetype_name="Basic Infantry",
        strongest_score=0.72,
        weakest_archetype_id="ELITE_HEROES",
        weakest_archetype_name="Elite Heroes",
        weakest_score=0.41,
    )

    assert recommendation.strongest_archetype_id == (
        "BASIC_INFANTRY"
    )
    assert recommendation.strongest_archetype_name == (
        "Basic Infantry"
    )
    assert recommendation.strongest_score == 0.72

    assert recommendation.weakest_archetype_id == (
        "ELITE_HEROES"
    )
    assert recommendation.weakest_archetype_name == (
        "Elite Heroes"
    )
    assert recommendation.weakest_score == 0.41

def test_builds_recommendation_from_archetype_summary():
    summary = (
        (
            "BASIC_INFANTRY",
            0.72,
        ),
        (
            "ELITE_INFANTRY",
            0.61,
        ),
        (
            "MID_TIER_HEROES",
            0.53,
        ),
        (
            "ELITE_HEROES",
            0.41,
        ),
    )

    recommendation = build_matchup_recommendation(
        archetype_summary=summary,
    )

    assert recommendation.strongest_archetype_id == (
        "BASIC_INFANTRY"
    )
    assert recommendation.strongest_archetype_name == (
        "Basic Infantry"
    )
    assert recommendation.strongest_score == 0.72

    assert recommendation.weakest_archetype_id == (
        "ELITE_HEROES"
    )
    assert recommendation.weakest_archetype_name == (
        "Elite Heroes"
    )
    assert recommendation.weakest_score == 0.41

def test_empty_archetype_summary_returns_none():
    recommendation = build_matchup_recommendation(
        archetype_summary=(),
    )

    assert recommendation is None