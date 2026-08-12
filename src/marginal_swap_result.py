"""
Project Palantír
================

File:
    marginal_swap_result.py

Purpose:
    Represents the scored effect of a one-for-one profile swap,
    including total objective change and per-capability changes.

Created:
    DEV-054 – Explainable Recommendations
"""

from dataclasses import dataclass

from profile_swap import ProfileSwap


@dataclass(frozen=True)
class MarginalCapabilityDelta:
    """
    Represents the change in one named objective capability.
    """

    name: str
    original_value: float
    alternative_value: float

    @property
    def delta(self) -> float:
        """
        Returns alternative minus original.
        """

        return (
            self.alternative_value
            - self.original_value
        )


@dataclass(frozen=True)
class MarginalSwapResult:
    """
    Represents the scoring impact of one profile swap.
    """

    swap: ProfileSwap
    original_score: float
    alternative_score: float
    capability_deltas: tuple[MarginalCapabilityDelta, ...] = ()

    @property
    def total_delta(self) -> float:
        """
        Returns alternative score minus original score.
        """

        return (
            self.alternative_score
            - self.original_score
        )