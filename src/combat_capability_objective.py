from dataclasses import dataclass

from army_combat_capability import (
    calculate_army_combat_capability,
)
from combat_benchmark import CombatBenchmark
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective


@dataclass(frozen=True)
class CombatCapabilityObjective(OptimiserObjective):
    benchmark: CombatBenchmark

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        return calculate_army_combat_capability(
            candidate.army,
            self.benchmark,
        )