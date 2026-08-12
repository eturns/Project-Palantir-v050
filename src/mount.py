"""
Project Palantír
================

File:
    mount.py

Purpose:
    Represents a mount that can be inherent to a Profile or
    granted through a ProfileOption.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043D – Iron Hills Import Integration
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Mount:
    """
    Represents a mount used by a configured Profile.

    Combat behaviour is implemented later. This entity currently
    establishes mount identity separately from ordinary Wargear.
    """

    id: str
    name: str
    base_size_mm: int = 40

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Mount ID cannot be empty."
            )

        if not self.name.strip():
            raise ValueError(
                "Mount name cannot be empty."
            )