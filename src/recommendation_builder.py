"""
Project Palantír
================

File:
    recommendation_builder.py

Purpose:
    Builds ranked explainable recommendation results from optimiser
    evaluations while preserving the optimiser's existing ranking rules.

Created:
    DEV-054 – Explainable Recommendations
"""

from objective_score import ObjectiveScore
from optimiser_evaluation import OptimiserEvaluation
from optimiser_ranking import rank_evaluations
from recommendation_result import RecommendationResult


def build_recommendations(
    evaluations: tuple[OptimiserEvaluation, ...],
    *,
    objective=None,
    marginal_swaps_by_candidate=None,
    sensitivity_stability_by_candidate=None,
) -> tuple[RecommendationResult, ...]:
    """
    Converts optimiser evaluations into ranked recommendation results.

    Ranking is delegated to the existing optimiser ranking layer so that
    equal scores preserve their original input order.

    If the supplied objective exposes a transparent score(candidate)
    method, its ObjectiveScore is preserved in the recommendation.
    Otherwise the optimiser evaluation score is used as the total.
    """

    ranked_evaluations = rank_evaluations(
        evaluations,
    )

    recommendations = []

    for index, evaluation in enumerate(
        ranked_evaluations,
        start=1,
    ):
        if (
            objective is not None
            and hasattr(objective, "score")
        ):
            objective_score = objective.score(
                evaluation.candidate,
            )
        else:
            objective_score = ObjectiveScore(
                total=evaluation.score,
            )

        if marginal_swaps_by_candidate is None:
            marginal_swaps = ()
        else:
            marginal_swaps = marginal_swaps_by_candidate.get(
                id(evaluation.candidate),
                (),
            )

        if sensitivity_stability_by_candidate is None:
            sensitivity_stability = None
        else:
            sensitivity_stability = (
                sensitivity_stability_by_candidate.get(
                    id(evaluation.candidate),
                )
            )

        recommendations.append(
            RecommendationResult(
                candidate=evaluation.candidate,
                rank=index,
                objective_score=objective_score,
                constraint_errors=tuple(
                    evaluation.errors,
                ),
                marginal_swaps=tuple(
                    marginal_swaps,
                ),
                sensitivity_stability=sensitivity_stability,
            )
        )

    return tuple(
        recommendations,
    )