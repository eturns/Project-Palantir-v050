from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_constraint import OptimiserConstraint


class RejectingConstraint(OptimiserConstraint):
    def validate(
        self,
        candidate: OptimiserCandidate,
    ) -> list[str]:
        return [
            "Candidate rejected.",
        ]


def test_optimiser_constraint_returns_validation_errors():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    constraint = RejectingConstraint()

    assert constraint.validate(candidate) == [
        "Candidate rejected.",
    ]