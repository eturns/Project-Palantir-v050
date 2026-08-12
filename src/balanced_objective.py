from dataclasses import dataclass

from balanced_score import (
    BALANCED_MEAN_WEIGHT,
    BALANCED_MINIMUM_WEIGHT,
)
from battlefield_effects_objective import (
    BattlefieldEffectsObjective,
)
from board_presence_objective import (
    BoardPresenceObjective,
)
from combat_capability_objective import (
    CombatCapabilityObjective,
)
from magic_objective import MagicObjective
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective
from objective_preset import ObjectivePreset
from resource_endurance_objective import (
    ResourceEnduranceObjective,
)


def build_balanced_objectives(
    *,
    army_list,
    combat_benchmark,
    resource_assumption,
):
    return {
        "board_presence": BoardPresenceObjective(
            army_list=army_list,
        ),
        "battlefield_effects": BattlefieldEffectsObjective(
            army_list=army_list,
        ),
        "combat_capability": CombatCapabilityObjective(
            benchmark=combat_benchmark,
        ),
        "magic": MagicObjective(
            army_list=army_list,
        ),
        "resource_endurance": ResourceEnduranceObjective(
            assumption=resource_assumption,
        ),
    }


@dataclass(frozen=True)
class BalancedObjective(OptimiserObjective):
    preset: ObjectivePreset
    army_list: object
    combat_benchmark: object
    resource_assumption: object

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        objectives = build_balanced_objectives(
            army_list=self.army_list,
            combat_benchmark=self.combat_benchmark,
            resource_assumption=self.resource_assumption,
        )

        scores_by_name = {
            name: objective.evaluate(candidate)
            for name, objective in objectives.items()
        }

        weighted_overall = sum(
            scores_by_name[weight.name]
            * weight.weight
            for weight in self.preset.weights
        )

        weakest_capability = min(
            scores_by_name[weight.name]
            for weight in self.preset.weights
        )

        return (
            weighted_overall
            * BALANCED_MEAN_WEIGHT
            + weakest_capability
            * BALANCED_MINIMUM_WEIGHT
        )