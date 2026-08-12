"""
Project Palantír
================

File:
    objective_score.py

Purpose:
    Represents transparent optimiser objective scores and
    their individual contributions.

Created:
    DEV-053 – Objective Functions and Weighting
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ObjectiveContribution:
    """
    Represents one named contribution to an objective score.
    """

    name: str
    value: float


@dataclass(frozen=True)
class ObjectiveScore:
    """
    Represents an overall optimiser score together with the
    contributions that produced it.
    """

    total: float
    contributions: tuple[ObjectiveContribution, ...] = ()