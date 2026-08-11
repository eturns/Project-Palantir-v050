"""
Project Palantír
================

File:
    optimiser_evaluation.py

Purpose:
    Represents the result of evaluating an optimiser candidate.

Created:
    DEV-051 – Optimiser Foundation
"""

from dataclasses import dataclass

from optimiser_candidate import OptimiserCandidate


@dataclass(frozen=True)
class OptimiserEvaluation:
    """
    Represents the evaluation of one optimiser candidate.
    """

    candidate: OptimiserCandidate
    score: float
    errors: tuple[str, ...] = ()