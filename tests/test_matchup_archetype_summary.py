from matchup_archetype_catalogue import (
    CANONICAL_MATCHUP_ARCHETYPES,
)
from matchup_archetype_summary import (
    build_matchup_archetype_summary,
)
from matchup_result import MatchupResult


def test_builds_score_for_every_canonical_archetype():
    results = (
        MatchupResult(
            target_profile_id="BENCH_ROHAN_WARRIOR",
            target_profile_name="Warrior of Rohan",
            score=0.40,
        ),
        MatchupResult(
            target_profile_id="BENCH_MORANNON_ORC",
            target_profile_name="Morannon Orc Warrior",
            score=0.60,
        ),
        MatchupResult(
            target_profile_id="BENCH_EREBOR_DWARF_WARRIOR",
            target_profile_name="Erebor Dwarf Warrior",
            score=0.50,
        ),
        MatchupResult(
            target_profile_id="BENCH_RIVENDELL_WARRIOR",
            target_profile_name="Rivendell Warrior",
            score=0.70,
        ),
        MatchupResult(
            target_profile_id="BENCH_ROHAN_CAPTAIN",
            target_profile_name="Captain of Rohan",
            score=0.45,
        ),
        MatchupResult(
            target_profile_id="BENCH_MINAS_TIRITH_CAPTAIN",
            target_profile_name="Captain of Minas Tirith",
            score=0.55,
        ),
        MatchupResult(
            target_profile_id="BENCH_MORANNON_ORC_CAPTAIN",
            target_profile_name="Morannon Orc Captain",
            score=0.65,
        ),
        MatchupResult(
            target_profile_id="BENCH_RIVENDELL_CAPTAIN",
            target_profile_name="Rivendell Captain",
            score=0.50,
        ),
        MatchupResult(
            target_profile_id="BENCH_IRON_HILLS_CAPTAIN",
            target_profile_name="Iron Hills Captain",
            score=0.60,
        ),
        MatchupResult(
            target_profile_id="BENCH_ELROND",
            target_profile_name="Elrond, Master of Rivendell",
            score=0.70,
        ),
    )

    summary = build_matchup_archetype_summary(
        results=results,
    )

    assert len(summary) == len(
        CANONICAL_MATCHUP_ARCHETYPES
    )

    assert {
        archetype_id
        for archetype_id, _ in summary
    } == {
        archetype.id
        for archetype in CANONICAL_MATCHUP_ARCHETYPES
    }