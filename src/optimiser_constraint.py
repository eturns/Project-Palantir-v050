"""
Project Palantír
================

File:
    optimiser_constraint.py

Purpose:
    Defines the interface used to validate optimiser candidates.

Created:
    DEV-051 – Optimiser Foundation
"""

from abc import ABC, abstractmethod

from optimiser_candidate import OptimiserCandidate


class OptimiserConstraint(ABC):
    """
    Defines a constraint applied to an optimiser candidate.
    """

    @abstractmethod
    def validate(
        self,
        candidate: OptimiserCandidate,
    ) -> list[str]:
        """
        Returns validation errors for a candidate.

        An empty list means the candidate satisfies
        the constraint.
        """