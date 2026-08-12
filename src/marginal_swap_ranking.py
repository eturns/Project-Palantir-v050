"""
Project Palantír
================

File:
    marginal_swap_ranking.py

Purpose:
    Ranks marginal swap results by their effect on the active
    optimiser objective.

Created:
    DEV-054 – Explainable Recommendations
"""

from marginal_swap_result import MarginalSwapResult


def rank_marginal_swaps(
    results: tuple[MarginalSwapResult, ...],
) -> tuple[MarginalSwapResult, ...]:
    """
    Returns marginal swaps ordered by highest total score delta first.

    Python's stable sort preserves the existing input order when
    multiple swaps have equal deltas.
    """

    return tuple(
        sorted(
            results,
            key=lambda result: result.total_delta,
            reverse=True,
        )
    )