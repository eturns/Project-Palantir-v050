from matchup_archetype import MatchupArchetype


def test_matchup_archetype_stores_name_and_profile_ids():
    archetype = MatchupArchetype(
        id="ELITE_HEROES",
        name="Elite Heroes",
        profile_ids=(
            "BENCH_RIVENDELL_CAPTAIN",
            "BENCH_IRON_HILLS_CAPTAIN",
            "BENCH_ELROND",
        ),
    )

    assert archetype.id == "ELITE_HEROES"
    assert archetype.name == "Elite Heroes"

    assert archetype.profile_ids == (
        "BENCH_RIVENDELL_CAPTAIN",
        "BENCH_IRON_HILLS_CAPTAIN",
        "BENCH_ELROND",
    )