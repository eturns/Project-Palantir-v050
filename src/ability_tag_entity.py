"""
Project Palantír
================

Ability Tag entity.
"""

from dataclasses import dataclass

from database.ability_tag import AbilityTag


@dataclass(frozen=True)
class AbilityTagEntity:
    """
    Represents an Ability Tag.
    """

    id: str
    name: str