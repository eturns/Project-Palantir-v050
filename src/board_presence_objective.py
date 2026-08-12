from dataclasses import dataclass

from army_list import ArmyList
from board_presence_input_builder import (
    build_board_presence_inputs,
)
from board_presence_score import (
    calculate_board_presence,
)
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective


@dataclass(frozen=True)
class BoardPresenceObjective(
    OptimiserObjective,
):
    army_list: ArmyList

    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        inputs = build_board_presence_inputs(
            candidate.army,
            self.army_list,
        )

        return calculate_board_presence(
            inputs,
        )