from matchup_archetype_catalogue import (
    CANONICAL_MATCHUP_ARCHETYPES,
)


def test_canonical_matchup_archetypes_cover_all_benchmark_profiles():
    expected_profile_ids = {
        "BENCH_ROHAN_WARRIOR",
        "BENCH_MORANNON_ORC",
        "BENCH_EREBOR_DWARF_WARRIOR",
        "BENCH_RIVENDELL_WARRIOR",
        "BENCH_ROHAN_CAPTAIN",
        "BENCH_MINAS_TIRITH_CAPTAIN",
        "BENCH_RIVENDELL_CAPTAIN",
        "BENCH_MORANNON_ORC_CAPTAIN",
        "BENCH_IRON_HILLS_CAPTAIN",
        "BENCH_ELROND",
    }

    actual_profile_ids = {
        profile_id
        for archetype in CANONICAL_MATCHUP_ARCHETYPES
        for profile_id in archetype.profile_ids
    }

    assert actual_profile_ids == expected_profile_ids


def test_canonical_matchup_archetypes_have_unique_ids():
    archetype_ids = tuple(
        archetype.id
        for archetype in CANONICAL_MATCHUP_ARCHETYPES
    )

    assert len(archetype_ids) == len(
        set(archetype_ids)
    )