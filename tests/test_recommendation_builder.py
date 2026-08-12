from army import Army
from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from optimiser_candidate import OptimiserCandidate
from optimiser_evaluation import OptimiserEvaluation
from recommendation_builder import build_recommendations

from marginal_swap_result import MarginalSwapResult
from profile_swap import ProfileSwap
from sensitivity_stability import SensitivityStability

class TransparentObjective:
    def score(
        self,
        candidate,
    ):
        return ObjectiveScore(
            total=0.75,
            contributions=(
                ObjectiveContribution(
                    name="board_presence",
                    value=0.80,
                ),
                ObjectiveContribution(
                    name="combat_capability",
                    value=0.70,
                ),
            ),
        )

class MarginalSwapObjective:
    def score(
        self,
        candidate,
    ):
        return ObjectiveScore(
            total=0.75,
        )


def test_build_recommendations_ranks_evaluations_and_assigns_ranks():
    low_candidate = OptimiserCandidate(
        army=Army(),
    )

    high_candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluations = (
        OptimiserEvaluation(
            candidate=low_candidate,
            score=0.40,
        ),
        OptimiserEvaluation(
            candidate=high_candidate,
            score=0.80,
        ),
    )

    recommendations = build_recommendations(
        evaluations,
    )

    assert len(recommendations) == 2

    assert recommendations[0].candidate == high_candidate
    assert recommendations[0].rank == 1
    assert recommendations[0].objective_score.total == 0.80

    assert recommendations[1].candidate == low_candidate
    assert recommendations[1].rank == 2
    assert recommendations[1].objective_score.total == 0.40


def test_build_recommendations_preserves_existing_tie_order():
    first_candidate = OptimiserCandidate(
        army=Army(),
    )

    second_candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluations = (
        OptimiserEvaluation(
            candidate=first_candidate,
            score=0.60,
        ),
        OptimiserEvaluation(
            candidate=second_candidate,
            score=0.60,
        ),
    )

    recommendations = build_recommendations(
        evaluations,
    )

    assert recommendations[0].candidate == first_candidate
    assert recommendations[0].rank == 1

    assert recommendations[1].candidate == second_candidate
    assert recommendations[1].rank == 2


def test_build_recommendations_uses_transparent_objective_score_when_available():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluations = (
        OptimiserEvaluation(
            candidate=candidate,
            score=0.75,
        ),
    )

    recommendations = build_recommendations(
        evaluations,
        objective=TransparentObjective(),
    )

    assert recommendations[0].objective_score == ObjectiveScore(
        total=0.75,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.80,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.70,
            ),
        ),
    )


def test_build_recommendations_still_uses_evaluation_score_without_objective():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluations = (
        OptimiserEvaluation(
            candidate=candidate,
            score=0.55,
        ),
    )

    recommendations = build_recommendations(
        evaluations,
    )

    assert recommendations[0].objective_score == ObjectiveScore(
        total=0.55,
    )

def test_build_recommendations_preserves_constraint_errors():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluation = OptimiserEvaluation(
        candidate=candidate,
        score=0.75,
        errors=(
            "Army exceeds points limit.",
        ),
    )

    recommendations = build_recommendations(
        (
            evaluation,
        ),
    )

    assert recommendations[0].constraint_errors == (
        "Army exceeds points limit.",
    )

def test_build_recommendations_preserves_constraint_errors():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluation = OptimiserEvaluation(
        candidate=candidate,
        score=0.75,
        errors=(
            "Army exceeds points limit.",
        ),
    )

    recommendations = build_recommendations(
        (
            evaluation,
        ),
    )

    assert recommendations[0].constraint_errors == (
        "Army exceeds points limit.",
    )

def test_build_recommendations_can_attach_marginal_swaps():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluation = OptimiserEvaluation(
        candidate=candidate,
        score=0.75,
    )

    marginal_swap = MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="profile_a",
            added_profile_id="profile_b",
        ),
        original_score=0.75,
        alternative_score=0.72,
    )

    recommendations = build_recommendations(
        (
            evaluation,
        ),
        marginal_swaps_by_candidate={
            id(candidate): (
                marginal_swap,
            ),
        },
    )

    assert recommendations[0].marginal_swaps == (
        marginal_swap,
    )

def test_build_recommendations_can_attach_sensitivity_stability():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    evaluation = OptimiserEvaluation(
        candidate=candidate,
        score=0.75,
    )

    stability = SensitivityStability(
        candidate_key="candidate_a:1",
        variant_count=10,
        rank_one_count=9,
        worst_rank=2,
    )

    recommendations = build_recommendations(
        (
            evaluation,
        ),
        sensitivity_stability_by_candidate={
            id(candidate): stability,
        },
    )

    assert recommendations[0].sensitivity_stability == stability