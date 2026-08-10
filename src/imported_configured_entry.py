"""
Project Palantír
================

File:
    imported_configured_entry.py

Purpose:
    Represents one configured model entry read from an external roster.

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
class ImportedConfiguredEntry:
    """
    Represents one configured entry from an external army export.

    Quantity describes how many identically configured models the
    roster entry contains. External option IDs describe the options
    selected on each individual model.
    """

    external_model_id: str
    external_option_ids: tuple[str, ...] = ()
    quantity: int = 1

    def __post_init__(self) -> None:
        if not self.external_model_id.strip():
            raise ValueError(
                "External model ID cannot be empty."
            )

        if self.quantity < 1:
            raise ValueError(
                "Imported configured-entry quantity "
                "must be at least one."
            )