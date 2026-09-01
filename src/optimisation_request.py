"""
Project Palantír
================

File:
    optimisation_request.py

Purpose:
    Defines the public input boundary for optimisation requests.

Created:
    DEV-052 – Legal Composition Enumeration
"""

from dataclasses import dataclass
from enum import Enum
from composition_spec import CompositionSpec

class OptimisationGoal(Enum):
    """
    Defines a high-level goal requested from the optimiser.

    Mathematical objective weights are assigned later
    by the objective-function layer.
    """

    BALANCED = "balanced"
    BOARD_PRESENCE = "board_presence"
    MAGIC = "magic"
    SCENARIO = "scenario"


@dataclass(frozen=True)
class OptimisationRequest:
    """
    Defines a high-level request submitted to the optimiser.

    The request describes what should be optimised,
    not how those goals are mathematically weighted.
    """

    army: str
    points_limit: int
    goals: tuple[OptimisationGoal, ...]
    composition_spec: CompositionSpec | None = None