"""
Project Palantír
================

File:
    marginal_swap_lookup.py

Purpose:
    Builds ranked marginal-swap results for each optimiser candidate.

Created:
    DEV-054 – Explainable Recommendations
"""

from marginal_swap_analysis import (
    analyse_marginal_swaps,
)
from marginal_swap_ranking import (
    rank_marginal_swaps,
)


def build_marginal_swap_lookup(
    *,
    candidates,
    objective,
    constraints=(),
):
    """
    Returns marginal-swap results for each candidate.

    Results are keyed by the in-memory candidate identity expected by
    recommendation_builder.build_recommendations().

    Each candidate's marginal swaps are ranked by total score delta.
    """

    lookup = {}

    for candidate in candidates:
        results = analyse_marginal_swaps(
            original=candidate,
            candidates=candidates,
            objective=objective,
            constraints=constraints,
        )

        lookup[
            id(candidate)
        ] = rank_marginal_swaps(
            results,
        )

    return lookup