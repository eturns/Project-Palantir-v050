from matchup_archetype import MatchupArchetype


CANONICAL_MATCHUP_ARCHETYPES = (
    MatchupArchetype(
        id="BASIC_INFANTRY",
        name="Basic Infantry",
        profile_ids=(
            "BENCH_ROHAN_WARRIOR",
            "BENCH_MORANNON_ORC",
        ),
    ),
    MatchupArchetype(
        id="ELITE_INFANTRY",
        name="Elite Infantry",
        profile_ids=(
            "BENCH_EREBOR_DWARF_WARRIOR",
            "BENCH_RIVENDELL_WARRIOR",
        ),
    ),
    MatchupArchetype(
        id="MID_TIER_HEROES",
        name="Mid-tier Heroes",
        profile_ids=(
            "BENCH_ROHAN_CAPTAIN",
            "BENCH_MINAS_TIRITH_CAPTAIN",
            "BENCH_MORANNON_ORC_CAPTAIN",
        ),
    ),
    MatchupArchetype(
        id="ELITE_HEROES",
        name="Elite Heroes",
        profile_ids=(
            "BENCH_RIVENDELL_CAPTAIN",
            "BENCH_IRON_HILLS_CAPTAIN",
            "BENCH_ELROND",
        ),
    ),
)