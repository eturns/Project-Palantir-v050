from dataclasses import dataclass

from combat_benchmark import CombatBenchmark
from combat_benchmark_profile_loader import (
    load_combat_benchmark_profiles,
)

@dataclass(frozen=True)
class WeightedCombatBenchmark:
    name: str
    benchmark: CombatBenchmark
    weight: float
    profile_id: str | None = None


@dataclass(frozen=True)
class CombatBenchmarkPortfolio:
    name: str
    benchmarks: tuple[WeightedCombatBenchmark, ...]

    def __post_init__(self):
        total = self.total_weight()

        if abs(total - 1.0) > 1e-9:
            raise ValueError(
                "Combat benchmark portfolio weights must total 1.0."
            )

    def total_weight(self) -> float:
        return sum(
            benchmark.weight
            for benchmark in self.benchmarks
        )

_COMBAT_BENCHMARK_PROFILES_BY_ID = {
    profile.id: profile
    for profile in load_combat_benchmark_profiles()
}


def _combat_benchmark_from_profile(
        profile_id: str,
    ) -> CombatBenchmark:
        profile = _COMBAT_BENCHMARK_PROFILES_BY_ID[
            profile_id
        ]

        return CombatBenchmark(
            fight=profile.fight,
            strength=profile.strength,
            defence=profile.defence,
            attacks=profile.attacks,
            wounds=profile.wounds,
        )

BALANCED_ALL_COMERS_V1 = CombatBenchmarkPortfolio(
    name="Balanced All-Comers v1",
    benchmarks=(
        WeightedCombatBenchmark(
            name="Warrior of Rohan",
            profile_id="BENCH_ROHAN_WARRIOR",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_ROHAN_WARRIOR",
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Morannon Orc",
            profile_id="BENCH_MORANNON_ORC",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_MORANNON_ORC",
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Erebor Dwarf Warrior",
            profile_id="BENCH_EREBOR_DWARF_WARRIOR",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_EREBOR_DWARF_WARRIOR",
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Rivendell Warrior",
            profile_id="BENCH_RIVENDELL_WARRIOR",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_RIVENDELL_WARRIOR",
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Rohan Captain",
            profile_id="BENCH_ROHAN_CAPTAIN",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_ROHAN_CAPTAIN",
            ),
            weight=0.08,
        ),
        WeightedCombatBenchmark(
            name="Minas Tirith Captain",
            profile_id="BENCH_MINAS_TIRITH_CAPTAIN",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_MINAS_TIRITH_CAPTAIN",
            ),
            weight=0.08,
        ),
        WeightedCombatBenchmark(
            name="Rivendell Captain",
            profile_id="BENCH_RIVENDELL_CAPTAIN",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_RIVENDELL_CAPTAIN",
            ),
            weight=0.08,
        ),
        WeightedCombatBenchmark(
            name="Morannon Orc Captain",
            profile_id="BENCH_MORANNON_ORC_CAPTAIN",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_MORANNON_ORC_CAPTAIN",
            ),
            weight=0.05,
        ),
        WeightedCombatBenchmark(
            name="Iron Hills Captain",
            profile_id="BENCH_IRON_HILLS_CAPTAIN",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_IRON_HILLS_CAPTAIN",
            ),
            weight=0.06,
        ),
        WeightedCombatBenchmark(
            name="Elrond",
            profile_id="BENCH_ELROND",
            benchmark=_combat_benchmark_from_profile(
                "BENCH_ELROND",
            ),
            weight=0.05,
        ),
    ),
)