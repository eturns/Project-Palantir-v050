"""
Project Palantír
================

File:
    army_entry.py

Purpose:
    Represents a single entry within an army list.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-007 – Army Entries
"""

from dataclasses import dataclass
from profiles import Profile
from profile_metrics_entity import ProfileMetrics
from profile_metrics import calculate_profile_metrics

@dataclass
class ArmyEntry:
    """
    Represents one profile within an army.

    Attributes:
        profile:
            The MESBG profile.

        quantity:
            Number of this profile included.
    """

    profile: Profile
    quantity: int = 1

    def __post_init__(self):
        """
        Validates the army entry after creation.
        """

        if self.quantity < 1:
            raise ValueError(
                "Quantity must be at least 1."
            )
    
    def total_points(self) -> int:
        """
        Returns the total points value of this army entry.
        """

        return self.total_attribute("points")

    def total_attribute(self,attribute: str,) -> int:
        """
        Returns the total value of an attribute
            across this army entry.
    """

        return (
            getattr(self.profile, attribute)
            * self.quantity
        )
    
    def get_attribute(self, attribute: str,):
        """
        Returns an attribute from this army entry's profile.
        """

        return getattr(self.profile, attribute)

    def profile_metrics(self) -> ProfileMetrics:
        """
        Returns the battlefield metrics for this profile.
        """
        from profile_metrics import (
            calculate_profile_metrics,
        )
        return calculate_profile_metrics(
            self.profile,
        )
