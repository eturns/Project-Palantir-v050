"""
Project Palantír
================

File:
    mapped_configured_entry.py

Purpose:
    Represents an imported configured entry after its external
    model ID has been mapped to a Palantír Profile ID.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043C – Configured-entry Import Model
"""

# ============================================================================
# Imports
# ============================================================================

from dataclasses import dataclass


# ============================================================================
# Classes
# ============================================================================

@dataclass(frozen=True)
class MappedConfiguredEntry:
    """
    Represents one imported roster entry after model-ID mapping.

    External option IDs are retained until they can be resolved
    against Palantír ProfileOption entities.
    """

    profile_id: str
    external_option_ids: tuple[str, ...] = ()
    quantity: int = 1

    def __post_init__(self) -> None:
        if not self.profile_id.strip():
            raise ValueError(
                "Profile ID cannot be empty."
            )

        if self.quantity < 1:
            raise ValueError(
                "Mapped configured-entry quantity "
                "must be at least one."
            )
        