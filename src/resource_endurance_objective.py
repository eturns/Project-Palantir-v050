from dataclasses import dataclass

from army_resource_endurance import (
    calculate_army_resource_endurance,
)
from army_resource_totals import (
    calculate_army_resource_totals,
)
from army_resource_trajectory import (
    calculate_army_resource_trajectory,
)
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)


@dataclass(frozen=True)
class ResourceEnduranceObjective(OptimiserObjective):
    assumption: ResourceEnduranceAssumption

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        resources = calculate_army_resource_totals(
            candidate.army,
        )

        trajectory = calculate_army_resource_trajectory(
            resources,
            self.assumption,
        )

        return calculate_army_resource_endurance(
            resources,
            trajectory,
        )