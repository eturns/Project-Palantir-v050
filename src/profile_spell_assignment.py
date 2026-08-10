"""
Project Palantír
================

File:
    profile_spell_assignment.py

Purpose:
    Represents a spell known by a profile.

Version:
    0.2.0-alpha

Created:
    DEV-025.1 – Profile Spell Assignments
"""

from dataclasses import dataclass

from spell import Spell


@dataclass(frozen=True)
class ProfileSpellAssignment:
    """
    Represents a spell known by a profile.
    """

    spell: Spell

    cast_value: int