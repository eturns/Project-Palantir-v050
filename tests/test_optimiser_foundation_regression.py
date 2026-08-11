from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_constraint import OptimiserConstraint
from optimiser_evaluator import evaluate_candidate
from optimiser_objective import OptimiserObjective
from optimiser_ranking import rank_evaluations


class ArmyPointsObjective(OptimiserObjective):
    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        return float(
            candidate.army.total_points()
        )


class MaximumPointsConstraint(OptimiserConstraint):
    def __init__(
        self,
        points_limit: int,
    ):
        self.points_limit = points_limit

    def validate(
        self,
        candidate: OptimiserCandidate,
    ) -> list[str]:
        if candidate.army.total_points() > self.points_limit:
            return [
                "Candidate exceeds points limit.",
            ]

        return []


def test_optimiser_foundation_evaluates_and_ranks_candidates():
    lower_army = Army()
    higher_army = Army()

    lower_candidate = OptimiserCandidate(
        army=lower_army,
    )

    higher_candidate = OptimiserCandidate(
        army=higher_army,
    )

    objective = ArmyPointsObjective()

    constraint = MaximumPointsConstraint(
        points_limit=700,
    )

    lower_evaluation = evaluate_candidate(
        candidate=lower_candidate,
        objective=objective,
        constraints=(
            constraint,
        ),
    )

    higher_evaluation = evaluate_candidate(
        candidate=higher_candidate,
        objective=objective,
        constraints=(
            constraint,
        ),
    )

    ranked = rank_evaluations(
        (
            lower_evaluation,
            higher_evaluation,
        )
    )

    assert lower_evaluation.errors == ()
    assert higher_evaluation.errors == ()

    assert ranked == (
        lower_evaluation,
        higher_evaluation,
    )