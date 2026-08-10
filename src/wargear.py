"""
Project Palantír
================

File:
    wargear.py

Purpose:
    Defines reusable Wargear entities used by Profiles and Profile Options.

Version:
    0.4.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-043B – Profile Wargear and Option Foundation
"""

# ============================================================================
# Imports
# ============================================================================

from dataclasses import dataclass, field

from special_rule import SpecialRule


# ============================================================================
# Classes
# ============================================================================

@dataclass(frozen=True)
class Wargear:
    """
    Represents one reusable item of Wargear.

    Wargear describes the equipment itself. Profile-specific legality
    and points costs belong to ProfileOption rather than this entity.
    """

    id: str
    name: str

    special_rules: list[SpecialRule] = field(
        default_factory=list,
    )

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Wargear ID cannot be empty.")

        if not self.name.strip():
            raise ValueError("Wargear name cannot be empty.")

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("wargear module loaded successfully.")