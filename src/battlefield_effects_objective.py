from dataclasses import dataclass

from battlefield_effects_input_builder import (
    build_battlefield_effects_inputs,
)
from battlefield_effects_score import (
    calculate_battlefield_effects_score,
)
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective


@dataclass(frozen=True)
class BattlefieldEffectsObjective(OptimiserObjective):
    army_list: object

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        inputs = build_battlefield_effects_inputs(
            candidate.army,
            self.army_list,
        )

        return calculate_battlefield_effects_score(
            inputs,
        )