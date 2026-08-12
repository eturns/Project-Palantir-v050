from dataclasses import dataclass

from army_list import ArmyList
from army_metric_densities import (
    calculate_army_metric_densities,
)
from objective_normalisation import (
    normalise_magic,
)
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective


@dataclass(frozen=True)
class MagicObjective(
    OptimiserObjective,
):
    army_list: ArmyList

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        densities = calculate_army_metric_densities(
            candidate.army,
            self.army_list,
        )

        return normalise_magic(
            magic_density=densities.magic,
        )