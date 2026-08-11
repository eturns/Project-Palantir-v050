"""
Project Palantír
================

File:
    optimiser_ranking.py

Purpose:
    Provides deterministic ranking of optimiser evaluations.

Created:
    DEV-051 – Optimiser Foundation
"""

from optimiser_evaluation import OptimiserEvaluation


def rank_evaluations(
    evaluations: tuple[OptimiserEvaluation, ...],
) -> tuple[OptimiserEvaluation, ...]:
    """
    Returns evaluations ranked from highest to lowest score.

    Equal scores preserve their original input order.
    """

    return tuple(
        sorted(
            evaluations,
            key=lambda evaluation: evaluation.score,
            reverse=True,
        )
    )