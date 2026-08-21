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
from owned_army_resource_initialization import (
    get_initial_owned_hero_resource_states,
)
from owned_resource_conversion_initialization import (
    get_initial_owned_resource_conversions,
)
from owned_resource_endurance import (
    calculate_owned_resource_endurance,
)
from owned_resource_use_permission_initialization import (
    get_initial_owned_resource_use_permissions,
)
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

        owned_states = get_initial_owned_hero_resource_states(
            candidate.army,
        )

        owned_permissions = get_initial_owned_resource_use_permissions(
            candidate.army,
        )

        owned_conversions = get_initial_owned_resource_conversions(
            candidate.army,
        )

        if owned_states:
            management_score = calculate_owned_resource_endurance(
                states=owned_states,
                assumption=self.assumption,
                permissions=owned_permissions,
                conversions=owned_conversions,
            )
        else:
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