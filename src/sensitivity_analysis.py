"""
Project Palantír
================

File:
    sensitivity_analysis.py

Purpose:
    Compares optimiser candidate rankings between a baseline objective
    and one controlled sensitivity variant.

Created:
    DEV-054 – Explainable Recommendations
"""

from optimiser_candidate_key import (
    build_candidate_key,
)
from optimiser_evaluation import OptimiserEvaluation
from optimiser_ranking import rank_evaluations
from sensitivity_result import SensitivityResult
from sensitivity_variants import SensitivityVariant


def _rank_candidates(
    *,
    candidates,
    objective,
):
    """
    Evaluates and ranks a candidate pool using the supplied objective.
    """

    evaluations = tuple(
        OptimiserEvaluation(
            candidate=candidate,
            score=objective.evaluate(
                candidate,
            ),
        )
        for candidate in candidates
    )

    return rank_evaluations(
        evaluations,
    )


def analyse_sensitivity_variant(
    *,
    candidates,
    baseline_objective,
    variant_objective,
    variant: SensitivityVariant,
) -> tuple[SensitivityResult, ...]:
    """
    Compares candidate ranks under a baseline objective and one
    sensitivity-variant objective.

    Results follow baseline ranking order.
    """

    if not candidates:
        return ()

    baseline_ranking = _rank_candidates(
        candidates=candidates,
        objective=baseline_objective,
    )

    variant_ranking = _rank_candidates(
        candidates=candidates,
        objective=variant_objective,
    )

    variant_rank_by_key = {
        build_candidate_key(
            evaluation.candidate,
        ): rank
        for rank, evaluation in enumerate(
            variant_ranking,
            start=1,
        )
    }

    return tuple(
        SensitivityResult(
            candidate_key=build_candidate_key(
                evaluation.candidate,
            ),
            baseline_rank=baseline_rank,
            variant_rank=variant_rank_by_key[
                build_candidate_key(
                    evaluation.candidate,
                )
            ],
            varied_capability=variant.varied_capability,
            baseline_weight=variant.baseline_weight,
            variant_weight=variant.variant_weight,
        )
        for baseline_rank, evaluation in enumerate(
            baseline_ranking,
            start=1,
        )
    )