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
from resource_capacity_score import (
    calculate_resource_capacity_score,
)
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)


CAPACITY_WEIGHT = 0.55
MANAGEMENT_WEIGHT = 0.45


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

        management_score = calculate_army_resource_endurance(
            resources,
            trajectory,
        )

        capacity_score = calculate_resource_capacity_score(
            might=resources.might,
            will=resources.will,
            fate=resources.fate,
            army_points=candidate.army.total_points(),
        )

        return (
            capacity_score
            * CAPACITY_WEIGHT
            +
            management_score
            * MANAGEMENT_WEIGHT
        )