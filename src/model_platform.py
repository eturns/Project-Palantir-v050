"""
Project Palantír
================

File:
    model_platform.py

Purpose:
    Represents a carrier, vehicle or War Beast that may support
    crew, occupants or passengers.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043D – Iron Hills Import Integration
"""

from dataclasses import dataclass
from enum import Enum


class PlatformType(Enum):
    """
    Identifies the broad structural type of a Platform.

    Behaviour for each type will be implemented later.
    """

    CHARIOT = "chariot"
    WAR_BEAST = "war_beast"
    VEHICLE = "vehicle"


@dataclass(frozen=True)
class Platform:
    """
    Represents a carrier, vehicle or War Beast.

    This entity currently establishes identity and broad type.
    Crew, passenger, movement and combat behaviour are deferred
    to later engine tickets.
    """

    id: str
    name: str
    platform_type: PlatformType

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Platform ID cannot be empty."
            )

        if not self.name.strip():
            raise ValueError(
                "Platform name cannot be empty."
            )