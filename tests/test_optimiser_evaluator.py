from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_constraint import OptimiserConstraint
from optimiser_evaluator import evaluate_candidate
from optimiser_objective import OptimiserObjective


class FixedScoreObjective(OptimiserObjective):
    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        return 4.25


class AcceptingConstraint(OptimiserConstraint):
    def validate(
        self,
        candidate: OptimiserCandidate,
    ) -> list[str]:
        return []


class RejectingConstraint(OptimiserConstraint):
    def validate(
        self,
        candidate: OptimiserCandidate,
    ) -> list[str]:
        return [
            "Candidate rejected.",
        ]


def test_evaluate_candidate_returns_score_for_valid_candidate():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluation = evaluate_candidate(
        candidate=candidate,
        objective=FixedScoreObjective(),
        constraints=(
            AcceptingConstraint(),
        ),
    )

    assert evaluation.candidate is candidate
    assert evaluation.score == 4.25
    assert evaluation.errors == ()


def test_evaluate_candidate_collects_constraint_errors():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluation = evaluate_candidate(
        candidate=candidate,
        objective=FixedScoreObjective(),
        constraints=(
            RejectingConstraint(),
        ),
    )

    assert evaluation.errors == (
        "Candidate rejected.",
    )