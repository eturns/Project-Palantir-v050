from army import Army
from optimiser_candidate import OptimiserCandidate
from optimiser_evaluation import OptimiserEvaluation
from optimiser_ranking import rank_evaluations


def test_rank_evaluations_orders_highest_score_first():
    lower = OptimiserEvaluation(
        candidate=OptimiserCandidate(
            army=Army(),
        ),
        score=2.0,
    )

    higher = OptimiserEvaluation(
        candidate=OptimiserCandidate(
            army=Army(),
        ),
        score=5.0,
    )

    ranked = rank_evaluations(
        (
            lower,
            higher,
        )
    )

    assert ranked == (
        higher,
        lower,
    )


def test_rank_evaluations_preserves_input_order_for_equal_scores():
    first = OptimiserEvaluation(
        candidate=OptimiserCandidate(
            army=Army(),
        ),
        score=3.0,
    )

    second = OptimiserEvaluation(
        candidate=OptimiserCandidate(
            army=Army(),
        ),
        score=3.0,
    )

    ranked = rank_evaluations(
        (
            first,
            second,
        )
    )

    assert ranked == (
        first,
        second,
    )