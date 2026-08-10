"""
Project Palantír
================

Represents a weighted relationship between an
ability and an Ability Tag.
"""

from dataclasses import dataclass

from ability_tag_entity import AbilityTagEntity


@dataclass(frozen=True)
class AbilityTagAssignment:
    """
    Represents a weighted Ability Tag assignment.
    """

    tag: AbilityTagEntity
    weight: float = 1.0