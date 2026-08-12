"""
Project Palantír
================

File:
    objective_capability_assessment.py

Purpose:
    Represents a classified optimiser capability contribution while
    preserving its name and normalised numeric score.

Created:
    DEV-054 – Explainable Recommendations
"""

from dataclasses import dataclass

from objective_capability_classifier import (
    classify_objective_capability,
)
from objective_score import ObjectiveContribution


@dataclass(frozen=True)
class ObjectiveCapabilityAssessment:
    """
    Structured assessment of one optimiser capability.
    """

    name: str
    value: float
    rating: str


def assess_objective_contribution(
    contribution: ObjectiveContribution,
) -> ObjectiveCapabilityAssessment:
    """
    Converts an objective contribution into a classified capability
    assessment.
    """

    return ObjectiveCapabilityAssessment(
        name=contribution.name,
        value=contribution.value,
        rating=classify_objective_capability(
            contribution.value,
        ),
    )