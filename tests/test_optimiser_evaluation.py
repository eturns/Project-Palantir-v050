from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_evaluation import OptimiserEvaluation


def test_optimiser_evaluation_stores_candidate_score_and_errors():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluation = OptimiserEvaluation(
        candidate=candidate,
        score=3.5,
        errors=(
            "Candidate rejected.",
        ),
    )

    assert evaluation.candidate is candidate
    assert evaluation.score == 3.5
    assert evaluation.errors == (
        "Candidate rejected.",
    )