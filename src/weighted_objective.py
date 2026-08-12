"""
Project Palantír
================

File:
    weighted_objective.py

Purpose:
    Combines weighted metric components into transparent
    optimiser objective scores.

Created:
    DEV-053 – Objective Functions and Weighting
"""

from dataclasses import dataclass

from objective_component import MetricObjectiveComponent
from objective_score import ObjectiveScore


@dataclass(frozen=True)
class WeightedObjective:
    """
    Defines an objective composed of weighted metric
    components.
    """

    components: tuple[MetricObjectiveComponent, ...]

    def evaluate(
        self,
        values: dict[str, float],
    ) -> ObjectiveScore:
        """
        Evaluates all configured components and returns the
        total score with its contribution breakdown.
        """

        contributions = tuple(
            component.evaluate(
                value=values[component.name]
            )
            for component in self.components
        )

        return ObjectiveScore(
            total=sum(
                contribution.value
                for contribution in contributions
            ),
            contributions=contributions,
        )