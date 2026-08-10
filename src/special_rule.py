"""
Project Palantír
================

File:
    special_rule.py

Purpose:
    Represents a Special Rule in MESBG.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-016 – Special Rules Framework
"""

from dataclasses import dataclass, field

from database.rule_category import RuleCategory
from ability_tag_entity import AbilityTagEntity
from ability_prerequisite_entity import AbilityPrerequisiteEntity
from ability_tag_assignment import AbilityTagAssignment


@dataclass(frozen=True)
class SpecialRule:
    """
    Represents a Special Rule in MESBG.
    """

    id: str
    name: str
    category: RuleCategory
    ability_tags: list[AbilityTagAssignment] = field(
        default_factory=list,
    )
    prerequisites: list[AbilityPrerequisiteEntity] = field(default_factory=list)