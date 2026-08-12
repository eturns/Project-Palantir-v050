"""
Project Palantír
================

File:
    recommendation_capabilities.py

Purpose:
    Identifies the strongest and weakest named objective contributions
    within an explainable optimiser score.

Created:
    DEV-054 – Explainable Recommendations
"""

from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)


def find_strongest_contributions(
    score: ObjectiveScore,
) -> tuple[ObjectiveContribution, ...]:
    """
    Returns all contributions tied for the highest value.

    Empty scores return an empty tuple.
    """

    if not score.contributions:
        return ()

    highest_value = max(
        contribution.value
        for contribution in score.contributions
    )

    return tuple(
        contribution
        for contribution in score.contributions
        if contribution.value == highest_value
    )


def find_weakest_contributions(
    score: ObjectiveScore,
) -> tuple[ObjectiveContribution, ...]:
    """
    Returns all contributions tied for the lowest value.

    Empty scores return an empty tuple.
    """

    if not score.contributions:
        return ()

    lowest_value = min(
        contribution.value
        for contribution in score.contributions
    )

    return tuple(
        contribution
        for contribution in score.contributions
        if contribution.value == lowest_value
    )
