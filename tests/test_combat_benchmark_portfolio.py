import pytest

from combat_benchmark import CombatBenchmark
from combat_benchmark_portfolio import (
    BALANCED_ALL_COMERS_V1,
    CombatBenchmarkPortfolio,
    WeightedCombatBenchmark,
)
from combat_benchmark_profile_loader import (
    load_combat_benchmark_profiles,
)

def test_combat_benchmark_portfolio_accepts_weights_totalling_one():
    portfolio = CombatBenchmarkPortfolio(
        name="Test Portfolio",
        benchmarks=(
            WeightedCombatBenchmark(
                name="Warrior",
                benchmark=CombatBenchmark(
                    fight=4,
                    strength=3,
                    defence=5,
                    attacks=1,
                    wounds=1,
                ),
                weight=0.60,
            ),
            WeightedCombatBenchmark(
                name="Hero",
                benchmark=CombatBenchmark(
                    fight=6,
                    strength=4,
                    defence=6,
                    attacks=2,
                    wounds=2,
                ),
                weight=0.40,
            ),
        ),
    )

    assert portfolio.total_weight() == pytest.approx(
        1.0,
    )


def test_combat_benchmark_portfolio_rejects_weights_not_totalling_one():
    with pytest.raises(
        ValueError,
        match="weights must total 1.0",
    ):
        CombatBenchmarkPortfolio(
            name="Invalid Portfolio",
            benchmarks=(
                WeightedCombatBenchmark(
                    name="Warrior",
                    benchmark=CombatBenchmark(
                        fight=4,
                        strength=3,
                        defence=5,
                        attacks=1,
                        wounds=1,
                    ),
                    weight=0.50,
                ),
                WeightedCombatBenchmark(
                    name="Hero",
                    benchmark=CombatBenchmark(
                        fight=6,
                        strength=4,
                        defence=6,
                        attacks=2,
                        wounds=2,
                    ),
                    weight=0.40,
                ),
            ),
        )

def test_balanced_all_comers_v1_has_expected_name():
    assert (
        BALANCED_ALL_COMERS_V1.name
        == "Balanced All-Comers v1"
    )


def test_balanced_all_comers_v1_contains_ten_real_profile_benchmarks():
    assert len(
        BALANCED_ALL_COMERS_V1.benchmarks
    ) == 10


def test_balanced_all_comers_v1_weights_total_one():
    assert (
        BALANCED_ALL_COMERS_V1.total_weight()
        == pytest.approx(1.0)
    )


def test_balanced_all_comers_v1_uses_sixty_percent_warrior_weight():
    warrior_names = {
        "Warrior of Rohan",
        "Morannon Orc",
        "Erebor Dwarf Warrior",
        "Rivendell Warrior",
    }

    warrior_weight = sum(
        entry.weight
        for entry in BALANCED_ALL_COMERS_V1.benchmarks
        if entry.name in warrior_names
    )

    assert warrior_weight == pytest.approx(
        0.60,
    )


def test_balanced_all_comers_v1_uses_forty_percent_hero_weight():
    hero_names = {
        "Rohan Captain",
        "Minas Tirith Captain",
        "Rivendell Captain",
        "Morannon Orc Captain",
        "Iron Hills Captain",
        "Elrond",
    }

    hero_weight = sum(
        entry.weight
        for entry in BALANCED_ALL_COMERS_V1.benchmarks
        if entry.name in hero_names
    )

    assert hero_weight == pytest.approx(
        0.40,
    )


def test_balanced_all_comers_v1_preserves_fight_breakpoints():
    fight_values = {
        entry.benchmark.fight
        for entry in BALANCED_ALL_COMERS_V1.benchmarks
    }

    assert fight_values == {
        3,
        4,
        5,
        6,
        7,
    }


def test_balanced_all_comers_v1_contains_rivendell_captain_f6_benchmark():
    rivendell_captain = next(
        entry
        for entry in BALANCED_ALL_COMERS_V1.benchmarks
        if entry.name == "Rivendell Captain"
    )

    assert rivendell_captain.benchmark == CombatBenchmark(
        fight=6,
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
    )


def test_balanced_all_comers_v1_contains_elrond_f7_major_hero_benchmark():
    elrond = next(
        entry
        for entry in BALANCED_ALL_COMERS_V1.benchmarks
        if entry.name == "Elrond"
    )

    assert elrond.benchmark == CombatBenchmark(
        fight=7,
        strength=4,
        defence=7,
        attacks=3,
        wounds=3,
    )

def test_balanced_all_comers_v1_benchmarks_reference_full_profiles():
    profiles_by_id = {
        profile.id: profile
        for profile in load_combat_benchmark_profiles()
    }

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

    assert {
        entry.profile_id
        for entry in BALANCED_ALL_COMERS_V1.benchmarks
    } == expected_profile_ids

    for entry in BALANCED_ALL_COMERS_V1.benchmarks:
        profile = profiles_by_id[entry.profile_id]

        assert entry.benchmark == CombatBenchmark(
            fight=profile.fight,
            strength=profile.strength,
            defence=profile.defence,
            attacks=profile.attacks,
            wounds=profile.wounds,
        )