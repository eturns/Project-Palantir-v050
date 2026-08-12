"""
Project Palantír
================

File:
    sensitivity_result.py

Purpose:
    Represents how an optimiser candidate's rank changes under
    a controlled objective-weight variation.

Created:
    DEV-054 – Explainable Recommendations
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SensitivityResult:
    """
    Represents one candidate's ranking response to one weight variation.
    """

    candidate_key: str
    baseline_rank: int
    variant_rank: int
    varied_capability: str
    baseline_weight: float
    variant_weight: float

    @property
    def rank_change(self) -> int:
        """
        Returns variant rank minus baseline rank.

        Positive values mean the candidate moved down the ranking.
        Negative values mean the candidate moved up.
        """

        return (
            self.variant_rank
            - self.baseline_rank
        )

    @property
    def rank_changed(self) -> bool:
        """
        Returns True when the candidate's rank changed.
        """

        return (
            self.variant_rank
            != self.baseline_rank
        )