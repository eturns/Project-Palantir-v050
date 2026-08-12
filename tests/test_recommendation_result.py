from army import Army
from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from optimiser_candidate import OptimiserCandidate
from recommendation_result import RecommendationResult
from analysis_constants import (
    EXCEPTIONAL,
    STRONG,
    WEAK,
)
from objective_capability_assessment import (
    ObjectiveCapabilityAssessment,
)
from marginal_swap_result import (
    MarginalSwapResult,
)
from profile_swap import ProfileSwap

from sensitivity_stability import SensitivityStability

def test_recommendation_result_stores_candidate_rank_and_objective_score():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    objective_score = ObjectiveScore(
        total=0.61,
        contributions=(
            ObjectiveContribution(
                name="board_presence",
                value=0.70,
            ),
            ObjectiveContribution(
                name="combat_capability",
                value=0.52,
            ),
        ),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=objective_score,
    )

    assert result.candidate == candidate
    assert result.rank == 1
    assert result.objective_score == objective_score


def test_recommendation_result_is_immutable():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.61,
        ),
    )

    try:
        result.rank = 2
        assert False, "RecommendationResult should be immutable."
    except AttributeError:
        pass

def test_recommendation_result_exposes_strongest_contributions():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.60,
            contributions=(
                ObjectiveContribution(
                    name="board_presence",
                    value=0.70,
                ),
                ObjectiveContribution(
                    name="combat_capability",
                    value=0.80,
                ),
                ObjectiveContribution(
                    name="magic",
                    value=0.40,
                ),
            ),
        ),
    )

    assert result.strengths == (
        ObjectiveContribution(
            name="combat_capability",
            value=0.80,
        ),
    )


def test_recommendation_result_exposes_weakest_contributions():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.60,
            contributions=(
                ObjectiveContribution(
                    name="board_presence",
                    value=0.70,
                ),
                ObjectiveContribution(
                    name="combat_capability",
                    value=0.80,
                ),
                ObjectiveContribution(
                    name="magic",
                    value=0.40,
                ),
            ),
        ),
    )

    assert result.weaknesses == (
        ObjectiveContribution(
            name="magic",
            value=0.40,
        ),
    )

def test_recommendation_result_exposes_classified_capabilities():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.70,
            contributions=(
                ObjectiveContribution(
                    name="board_presence",
                    value=0.68,
                ),
                ObjectiveContribution(
                    name="combat_capability",
                    value=0.83,
                ),
                ObjectiveContribution(
                    name="magic",
                    value=0.31,
                ),
            ),
        ),
    )

    assert result.capabilities == (
        ObjectiveCapabilityAssessment(
            name="board_presence",
            value=0.68,
            rating=STRONG,
        ),
        ObjectiveCapabilityAssessment(
            name="combat_capability",
            value=0.83,
            rating=EXCEPTIONAL,
        ),
        ObjectiveCapabilityAssessment(
            name="magic",
            value=0.31,
            rating=WEAK,
        ),
    )


def test_recommendation_result_with_no_contributions_has_no_capabilities():
    candidate = OptimiserCandidate(
            army=Army(),
        )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.70,
        ),
    )

    assert result.capabilities == ()

def test_recommendation_result_defaults_to_no_constraint_errors():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.75,
        ),
    )

    assert result.constraint_errors == ()


def test_recommendation_result_stores_constraint_errors():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.75,
        ),
        constraint_errors=(
            "Army exceeds points limit.",
            "Required profile missing.",
        ),
    )

    assert result.constraint_errors == (
        "Army exceeds points limit.",
        "Required profile missing.",
    )

def test_recommendation_result_defaults_to_no_marginal_swaps():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.75,
        ),
    )

    assert result.marginal_swaps == ()


def test_recommendation_result_stores_marginal_swaps():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    marginal_swap = MarginalSwapResult(
        swap=ProfileSwap(
            removed_profile_id="profile_a",
            added_profile_id="profile_b",
        ),
        original_score=0.75,
        alternative_score=0.72,
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.75,
        ),
        marginal_swaps=(
            marginal_swap,
        ),
    )

    assert result.marginal_swaps == (
        marginal_swap,
    )

def test_recommendation_result_defaults_to_no_sensitivity_stability():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.75,
        ),
    )

    assert result.sensitivity_stability is None


def test_recommendation_result_stores_sensitivity_stability():
    candidate = OptimiserCandidate(
        army=Army(),
    )

    stability = SensitivityStability(
        candidate_key="candidate_a:1",
        variant_count=10,
        rank_one_count=9,
        worst_rank=2,
    )

    result = RecommendationResult(
        candidate=candidate,
        rank=1,
        objective_score=ObjectiveScore(
            total=0.75,
        ),
        sensitivity_stability=stability,
    )

    assert result.sensitivity_stability == stability