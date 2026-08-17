from dataclasses import dataclass

from army_combat_capability import (
    calculate_army_combat_capability,
)
from combat_benchmark import CombatBenchmark
from combat_benchmark_portfolio import (
    CombatBenchmarkPortfolio,
)
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective


@dataclass(frozen=True)
class CombatCapabilityObjective(OptimiserObjective):
    benchmark: (
        CombatBenchmark
        | CombatBenchmarkPortfolio
    )

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        if isinstance(
            self.benchmark,
            CombatBenchmarkPortfolio,
        ):
            return sum(
                calculate_army_combat_capability(
                    candidate.army,
                    weighted_benchmark.benchmark,
                )
                * weighted_benchmark.weight
                for weighted_benchmark
                in self.benchmark.benchmarks
            )

        return calculate_army_combat_capability(
            candidate.army,
            self.benchmark,
        )