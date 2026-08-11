from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_objective import OptimiserObjective


class FixedScoreObjective(OptimiserObjective):
    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        return 3.5


def test_optimiser_objective_evaluates_candidate():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    objective = FixedScoreObjective()

    assert objective.evaluate(candidate) == 3.5