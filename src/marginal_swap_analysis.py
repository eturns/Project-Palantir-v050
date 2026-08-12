"""
Project Palantír
================

File:
    marginal_swap_analysis.py

Purpose:
    Analyses one-swap alternatives for an optimiser candidate and
    returns their transparent scored effects.

Created:
    DEV-054 – Explainable Recommendations
"""

from marginal_swap_builder import (
    build_marginal_swap_result,
)
from marginal_swap_finder import (
    find_marginal_alternatives,
)
from optimiser_candidate import OptimiserCandidate
from profile_swap_detection import (
    detect_profile_swap,
)


def analyse_marginal_swaps(
    *,
    original: OptimiserCandidate,
    candidates: tuple[OptimiserCandidate, ...],
    objective,
    constraints=(),
):
    """
    Scores every candidate that differs from the original by exactly
    one profile swap and satisfies all supplied optimiser constraints.

    Candidate pool order is preserved.
    """

    original_score = objective.score(
        original,
    )

    alternatives = find_marginal_alternatives(
        original,
        candidates,
    )

    results = []

    for alternative in alternatives:
        constraint_errors = []

        for constraint in constraints:
            constraint_errors.extend(
                constraint.validate(
                    alternative,
                )
            )

        if constraint_errors:
            continue

        swap = detect_profile_swap(
            original,
            alternative,
        )

        alternative_score = objective.score(
            alternative,
        )

        results.append(
            build_marginal_swap_result(
                swap=swap,
                original_score=original_score,
                alternative_score=alternative_score,
            )
        )

    return tuple(
        results,
    )