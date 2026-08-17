from dataclasses import dataclass

from combat_benchmark import CombatBenchmark


@dataclass(frozen=True)
class WeightedCombatBenchmark:
    name: str
    benchmark: CombatBenchmark
    weight: float


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

BALANCED_ALL_COMERS_V1 = CombatBenchmarkPortfolio(
    name="Balanced All-Comers v1",
    benchmarks=(
        WeightedCombatBenchmark(
            name="Warrior of Rohan",
            benchmark=CombatBenchmark(
                fight=3,
                strength=3,
                defence=4,
                attacks=1,
                wounds=1,
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Morannon Orc",
            benchmark=CombatBenchmark(
                fight=3,
                strength=4,
                defence=5,
                attacks=1,
                wounds=1,
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Erebor Dwarf Warrior",
            benchmark=CombatBenchmark(
                fight=4,
                strength=3,
                defence=6,
                attacks=1,
                wounds=1,
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Rivendell Warrior",
            benchmark=CombatBenchmark(
                fight=5,
                strength=3,
                defence=5,
                attacks=1,
                wounds=1,
            ),
            weight=0.15,
        ),
        WeightedCombatBenchmark(
            name="Rohan Captain",
            benchmark=CombatBenchmark(
                fight=4,
                strength=4,
                defence=5,
                attacks=2,
                wounds=2,
            ),
            weight=0.08,
        ),
        WeightedCombatBenchmark(
            name="Minas Tirith Captain",
            benchmark=CombatBenchmark(
                fight=5,
                strength=4,
                defence=7,
                attacks=2,
                wounds=2,
            ),
            weight=0.08,
        ),
        WeightedCombatBenchmark(
            name="Rivendell Captain",
            benchmark=CombatBenchmark(
                fight=6,
                strength=4,
                defence=6,
                attacks=2,
                wounds=2,
            ),
            weight=0.08,
        ),
        WeightedCombatBenchmark(
            name="Morannon Orc Captain",
            benchmark=CombatBenchmark(
                fight=4,
                strength=5,
                defence=6,
                attacks=2,
                wounds=2,
            ),
            weight=0.05,
        ),
        WeightedCombatBenchmark(
            name="Iron Hills Captain",
            benchmark=CombatBenchmark(
                fight=5,
                strength=4,
                defence=8,
                attacks=2,
                wounds=2,
            ),
            weight=0.06,
        ),
        WeightedCombatBenchmark(
            name="Elrond",
            benchmark=CombatBenchmark(
                fight=7,
                strength=4,
                defence=7,
                attacks=3,
                wounds=3,
            ),
            weight=0.05,
        ),
    ),
)
    