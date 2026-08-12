"""
Project Palantír
================

File:
    profile_swap.py

Purpose:
    Represents a one-for-one profile replacement between two
    optimiser candidate armies.

Created:
    DEV-054 – Explainable Recommendations
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfileSwap:
    """
    Represents one profile instance being removed and one different
    profile instance being added.
    """

    removed_profile_id: str
    added_profile_id: str

    def __post_init__(self):
        if self.removed_profile_id == self.added_profile_id:
            raise ValueError(
                "A profile swap must remove and add different profiles."
            )