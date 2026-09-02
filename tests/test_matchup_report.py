from matchup_report import (
    MatchupReport,
    build_matchup_report,
)
from matchup_result import MatchupResult
from matchup_recommendation import MatchupRecommendation


def test_matchup_report_stores_recommendation_and_profile_results():
    strongest_results = (
        MatchupResult(
            target_profile_id="BENCH_ROHAN_WARRIOR",
            target_profile_name="Warrior of Rohan",
            score=0.72,
        ),
        MatchupResult(
            target_profile_id="BENCH_MORANNON_ORC",
            target_profile_name="Morannon Orc Warrior",
            score=0.68,
        ),
    )

    weakest_results = (
        MatchupResult(
            target_profile_id="BENCH_RIVENDELL_CAPTAIN",
            target_profile_name="Rivendell Captain",
            score=0.44,
        ),
        MatchupResult(
            target_profile_id="BENCH_ELROND",
            target_profile_name="Elrond, Master of Rivendell",
            score=0.38,
        ),
    )

    report = MatchupReport(
        strongest_archetype_id="BASIC_INFANTRY",
        strongest_archetype_name="Basic Infantry",
        strongest_score=0.70,
        strongest_results=strongest_results,
        weakest_archetype_id="ELITE_HEROES",
        weakest_archetype_name="Elite Heroes",
        weakest_score=0.41,
        weakest_results=weakest_results,
    )

    assert report.strongest_archetype_id == (
        "BASIC_INFANTRY"
    )
    assert report.strongest_archetype_name == (
        "Basic Infantry"
    )
    assert report.strongest_score == 0.70
    assert report.strongest_results == strongest_results

    assert report.weakest_archetype_id == (
        "ELITE_HEROES"
    )
    assert report.weakest_archetype_name == (
        "Elite Heroes"
    )
    assert report.weakest_score == 0.41
    assert report.weakest_results == weakest_results

def test_builds_matchup_report_from_recommendation_and_results():
    results = (
        MatchupResult(
            target_profile_id="BENCH_ROHAN_WARRIOR",
            target_profile_name="Warrior of Rohan",
            score=0.72,
        ),
        MatchupResult(
            target_profile_id="BENCH_MORANNON_ORC",
            target_profile_name="Morannon Orc Warrior",
            score=0.68,
        ),
        MatchupResult(
            target_profile_id="BENCH_RIVENDELL_CAPTAIN",
            target_profile_name="Rivendell Captain",
            score=0.44,
        ),
        MatchupResult(
            target_profile_id="BENCH_IRON_HILLS_CAPTAIN",
            target_profile_name="Iron Hills Captain",
            score=0.41,
        ),
        MatchupResult(
            target_profile_id="BENCH_ELROND",
            target_profile_name="Elrond, Master of Rivendell",
            score=0.38,
        ),
    )

    recommendation = MatchupRecommendation(
        strongest_archetype_id="BASIC_INFANTRY",
        strongest_archetype_name="Basic Infantry",
        strongest_score=0.70,
        weakest_archetype_id="ELITE_HEROES",
        weakest_archetype_name="Elite Heroes",
        weakest_score=0.41,
    )

    report = build_matchup_report(
        recommendation=recommendation,
        results=results,
    )

    assert report.strongest_archetype_id == (
        "BASIC_INFANTRY"
    )
    assert report.weakest_archetype_id == (
        "ELITE_HEROES"
    )

    assert {
        result.target_profile_id
        for result in report.strongest_results
    } == {
        "BENCH_ROHAN_WARRIOR",
        "BENCH_MORANNON_ORC",
    }

    assert {
        result.target_profile_id
        for result in report.weakest_results
    } == {
        "BENCH_RIVENDELL_CAPTAIN",
        "BENCH_IRON_HILLS_CAPTAIN",
        "BENCH_ELROND",
    }