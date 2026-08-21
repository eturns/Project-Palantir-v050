"""
Project Palantír
================

File:
    models.py

Purpose:
    Defines the core data structures used throughout the engine.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-003 – The First Model
"""

# ============================================================================
# Imports
# ============================================================================

from dataclasses import dataclass, field 
from special_rule import SpecialRule
from heroic_action import HeroicAction
from spell import Spell
from profile_spell_assignment import (
    ProfileSpellAssignment,
)
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)
from profile_option import ProfileOption

from wargear import Wargear
from mount import Mount
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from resource_conversion import ResourceConversion
# ============================================================================
# Constants
# ============================================================================

# (None yet)

# ============================================================================
# Classes
# ============================================================================

@dataclass
class Profile:
    """
    Represents a single Middle-earth Strategy Battle Game model.
    """

    id: str
    name: str
    points: int

    movement: int
    fight: int
    shooting: str
    strength: int
    defence: int
    attacks: int
    wounds: int
    
    courage: str
    intelligence: str

    might: int
    will: int
    fate: int

    max_in_army: int

    base_size_mm: int = 25

    keywords: set[str] = field(
        default_factory=set,
    )

    profile_options: list[ProfileOption] = field(
        default_factory=list,
    )

    default_wargear: list[Wargear] = field(
        default_factory=list,
    )

    default_mount: Mount | None = None

    special_rules: list[ProfileSpecialRuleAssignment] = field(
        default_factory=list,
    )
    
    heroic_actions: list[HeroicAction] = field(default_factory=list)
    spells: list[ProfileSpellAssignment] = field(
        default_factory=list,
    )

    special_resource_permissions: tuple[
        tuple[ResourceType, ResourceUse],
        ...,
    ] = ()

    special_resource_conversions: tuple[
        ResourceConversion,
        ...,
    ] = ()
# ============================================================================
# Functions
# ============================================================================

# (None yet)

# ============================================================================
# Main Execution
# ============================================================================

if __name__ == "__main__":
    print("profile module loaded successfully.")