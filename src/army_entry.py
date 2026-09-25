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
from configured_profile import ConfiguredProfile
from profiles import Profile
from profile_metrics_entity import ProfileMetrics
from profile_metrics import calculate_profile_metrics
from siege_engine_profile import SiegeEngineProfile

@dataclass(init=False)
class ArmyEntry:
    """
    Represents one profile within an army.

    Attributes:
        profile:
            The MESBG profile.

        quantity:
            Number of this profile included.
    """

    configured_profile: ConfiguredProfile | None
    siege_engine_profile: SiegeEngineProfile | None
    quantity: int = 1
    warband_id: str | None = None

    def __init__(
        self,
        configured_profile: ConfiguredProfile | None = None,
        quantity: int = 1,
        profile: Profile | None = None,
        warband_id: str | None = None,
        siege_engine_profile: SiegeEngineProfile | None = None,
        points_override: int | None = None
    ) -> None:
        """
        Creates an ArmyEntry from either an authoritative
        ConfiguredProfile or a legacy bare Profile.

        Bare Profiles are wrapped in an unconfigured
        ConfiguredProfile for backward compatibility.
        """

        profile_sources = sum(
            source is not None
            for source in (
                configured_profile,
                profile,
                siege_engine_profile,
            )
        )

        if profile_sources != 1:
            raise ValueError(
                "ArmyEntry requires exactly one profile source."
            )

        if profile is not None:
            configured_profile = ConfiguredProfile(
                profile=profile,
            )

        self.configured_profile = configured_profile
        self.siege_engine_profile = siege_engine_profile
        self.quantity = quantity
        self.warband_id = warband_id
        self.points_override = points_override

        self.__post_init__()

    @property
    def counts_as_model(self) -> bool:
        return self.siege_engine_profile is None

    def __post_init__(self):
        """
        Validates the army entry after creation.
        """

        if self.quantity < 1:
            raise ValueError(
                "Quantity must be at least 1."
            )

        if (
            self.points_override is not None
            and self.points_override < 0
        ):
            raise ValueError(
                "Points override must not be negative."
            )

    @property
    def profile(self) -> Profile:
        """
        Returns the canonical base Profile for compatibility
        with existing Army-level consumers.
        """

        return self.configured_profile.profile
    
    def total_points(self) -> int:
        if self.points_override is not None:
            return (
                self.points_override
                * self.quantity
            )

        if self.siege_engine_profile is not None:
            return (
                self.siege_engine_profile.points
                * self.quantity
            )

        return (
            self.configured_profile.points
            * self.quantity
        )
    
    def get_attribute(
        self,
        attribute: str,
    ):
        """
        Returns the effective value of an analytical
        characteristic for this army entry.

        Characteristics affected by static configuration
        are resolved from ConfiguredProfile. All other
        characteristics fall back to the canonical
        base Profile.
        """

        configured_attributes = {
            "movement": "effective_movement",
            "defence": "effective_defence",
            "shooting": "effective_shooting",
            "base_size_mm": "effective_base_size_mm",
        }

        configured_attribute = (
            configured_attributes.get(attribute)
        )

        if configured_attribute is not None:
            return getattr(
                self.configured_profile,
                configured_attribute,
            )

        return getattr(
            self.profile,
            attribute,
        )


    def total_attribute(
        self,
        attribute: str,
    ) -> int:
        """
        Returns the total effective value of an analytical
        characteristic across this army entry.
        """

        return (
            self.get_attribute(attribute)
            * self.quantity
        )

    def profile_metrics(self) -> ProfileMetrics:
        """
        Returns the battlefield metrics for this profile.
        """
        from profile_metrics import (
            calculate_profile_metrics,
        )
        return calculate_profile_metrics(
            self.configured_profile,
        )
