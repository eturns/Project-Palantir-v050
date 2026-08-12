"""
Project Palantír
================

File:
    objective_component.py

Purpose:
    Defines reusable weighted metric components for
    optimiser objective scoring.

Created:
    DEV-053 – Objective Functions and Weighting
"""

from dataclasses import dataclass

from metric_normalisation import normalise_linear
from objective_score import ObjectiveContribution


@dataclass(frozen=True)
class MetricObjectiveComponent:
    """
    Defines one weighted metric contribution to an
    optimiser objective.
    """

    name: str
    minimum: float
    maximum: float
    weight: float

    def evaluate(
        self,
        value: float,
    ) -> ObjectiveContribution:
        """
        Normalises a raw metric value and applies the
        configured objective weight.
        """

        normalised = normalise_linear(
            value=value,
            minimum=self.minimum,
            maximum=self.maximum,
        )

        return ObjectiveContribution(
            name=self.name,
            value=normalised * self.weight,
        )