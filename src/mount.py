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

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Mount:
    """
    Represents a Cavalry Mount and its battlefield profile.
    """

    id: str
    name: str
    movement: int
    fight: int
    shooting: str
    strength: int
    defence: int
    attacks: int
    wounds: int
    courage: str
    intelligence: str
    base_size_mm: int = 40
    races: frozenset[str] = field(
        default_factory=frozenset,
    )
    special_rule_ids: frozenset[str] = field(
        default_factory=frozenset,
    )

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Mount ID cannot be empty."
            )

        if not self.name.strip():
            raise ValueError(
                "Mount name cannot be empty."
            )

        if self.movement <= 0:
            raise ValueError(
                "Mount Movement must be positive."
            )

        if self.fight < 0:
            raise ValueError(
                "Mount Fight cannot be negative."
            )

        if self.strength < 0:
            raise ValueError(
                "Mount Strength cannot be negative."
            )

        if self.defence < 0:
            raise ValueError(
                "Mount Defence cannot be negative."
            )

        if self.attacks < 0:
            raise ValueError(
                "Mount Attacks cannot be negative."
            )

        if self.wounds < 1:
            raise ValueError(
                "Mount Wounds must be at least 1."
            )