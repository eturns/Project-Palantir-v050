from matchup_report import MatchupReport
from matchup_report_formatter import (
    format_matchup_report,
)
from matchup_result import MatchupResult


def test_formats_matchup_report_with_strongest_and_weakest_sections():
    report = MatchupReport(
        strongest_archetype_id="BASIC_INFANTRY",
        strongest_archetype_name="Basic Infantry",
        strongest_score=0.70,
        strongest_results=(
            MatchupResult(
                target_profile_id="BENCH_ROHAN_WARRIOR",
                target_profile_name="Warrior of Rohan",
                score=0.72,
                offensive_score=0.68,
                defensive_score=0.76,
            ),
            MatchupResult(
                target_profile_id="BENCH_MORANNON_ORC",
                target_profile_name="Morannon Orc Warrior",
                score=0.68,
                offensive_score=0.64,
                defensive_score=0.72,
            ),
        ),
        weakest_archetype_id="ELITE_HEROES",
        weakest_archetype_name="Elite Heroes",
        weakest_score=0.41,
        weakest_results=(
            MatchupResult(
                target_profile_id="BENCH_ELROND",
                target_profile_name="Elrond, Master of Rivendell",
                score=0.38,
                offensive_score=0.28,
                defensive_score=0.48,
            ),
        ),
    )

    text = format_matchup_report(
        report=report,
    )

    assert "Strongest Matchup" in text
    assert "Basic Infantry" in text
    assert "0.700" in text

    assert "Warrior of Rohan" in text
    assert "Morannon Orc Warrior" in text

    assert "Weakest Matchup" in text
    assert "Elite Heroes" in text
    assert "0.410" in text

    assert "Elrond, Master of Rivendell" in text