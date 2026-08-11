"""
Project Palantír
================

File:
    optimiser_objective.py

Purpose:
    Defines the interface used to score optimiser candidates.

Created:
    DEV-051 – Optimiser Foundation
"""

from abc import ABC, abstractmethod

from optimiser_candidate import OptimiserCandidate


class OptimiserObjective(ABC):
    """
    Defines an objective used to evaluate optimiser candidates.
    """

    @abstractmethod
    def evaluate(
        self,
        candidate: OptimiserCandidate,
    ) -> float:
        """
        Returns the score assigned to a candidate.
        """