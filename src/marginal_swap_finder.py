"""
Project Palantír
================

File:
    marginal_swap_finder.py

Purpose:
    Finds optimiser candidate armies that differ from a reference
    candidate by exactly one profile swap.

Created:
    DEV-054 – Explainable Recommendations
"""

from optimiser_candidate import OptimiserCandidate
from profile_swap_detection import detect_profile_swap


def find_marginal_alternatives(
    original: OptimiserCandidate,
    candidates: tuple[OptimiserCandidate, ...],
) -> tuple[OptimiserCandidate, ...]:
    """
    Returns candidate armies that differ from the original by exactly
    one valid profile swap.

    Candidate pool order is preserved.
    """

    return tuple(
        candidate
        for candidate in candidates
        if (
            candidate is not original
            and detect_profile_swap(
                original,
                candidate,
            )
            is not None
        )
    )