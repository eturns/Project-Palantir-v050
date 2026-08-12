"""
Project Palantír
================

File:
    marginal_swap_builder.py

Purpose:
    Builds the scored impact of a one-for-one profile swap from two
    transparent objective scores.

Created:
    DEV-054 – Explainable Recommendations
"""

from marginal_swap_result import (
    MarginalCapabilityDelta,
    MarginalSwapResult,
)
from objective_score import ObjectiveScore
from profile_swap import ProfileSwap


def build_marginal_swap_result(
    *,
    swap: ProfileSwap,
    original_score: ObjectiveScore,
    alternative_score: ObjectiveScore,
) -> MarginalSwapResult:
    """
    Builds a marginal swap result from two comparable objective scores.

    Capabilities are matched by name while preserving the contribution
    order of the original score.

    Raises:
        ValueError:
            If the two scores do not expose the same named capability set.
    """

    original_by_name = {
        contribution.name: contribution
        for contribution in original_score.contributions
    }

    alternative_by_name = {
        contribution.name: contribution
        for contribution in alternative_score.contributions
    }

    if set(original_by_name) != set(alternative_by_name):
        raise ValueError(
            "Marginal swap scores must contain the same capability set."
        )

    capability_deltas = tuple(
        MarginalCapabilityDelta(
            name=contribution.name,
            original_value=contribution.value,
            alternative_value=alternative_by_name[
                contribution.name
            ].value,
        )
        for contribution in original_score.contributions
    )

    return MarginalSwapResult(
        swap=swap,
        original_score=original_score.total,
        alternative_score=alternative_score.total,
        capability_deltas=capability_deltas,
    )