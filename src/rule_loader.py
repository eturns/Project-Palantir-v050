"""
Project Palantír
================

File:
    rule_loader.py

Purpose:
    Loads MESBG profile data from CSV files.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-004 – Data Layer
"""

# ============================================================================
# Imports
# ============================================================================

import csv
from special_rule import SpecialRule
from heroic_action import HeroicAction
from spell import Spell
from database.rule_category import RuleCategory
from ability_tag_entity import AbilityTagEntity
from ability_prerequisite_entity import AbilityPrerequisiteEntity


# ============================================================================
# Constants
# ============================================================================

# (None yet)

# ============================================================================
# Functions
# ============================================================================

def load_special_rules() -> dict[str, SpecialRule]:
    """
    Loads every Special Rule from the database.

    Returns:
        A dictionary containing every SpecialRule object,
        keyed by its unique ID.
    """

    special_rules: dict[str,SpecialRule] = {}

    with open(
        "data/rules/special_rules.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            special_rule = SpecialRule(
                id=row["id"],
                name=row["name"],
                category=RuleCategory[row["category"]],
            )

            special_rules[special_rule.id] = special_rule

    return special_rules

def load_heroic_actions() -> dict[str, HeroicAction]:
    """
    Loads every Heroic Action from the database.

    Returns:
        A dictionary containing every HeroicAction object,
        keyed by its unique ID.
    """

    heroic_actions: dict[str,HeroicAction] = {}

    with open(
        "data/rules/heroic_actions.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            heroic_action = HeroicAction(
                id=row["id"],
                name=row["name"],
                category=RuleCategory[row["category"]],
            )

            heroic_actions[heroic_action.id] = heroic_action

    return heroic_actions

def load_spells() -> dict[str, Spell]:
    """
    Loads every Spell from the database.

    Returns:
        A dictionary containing every Spell object,
        keyed by its unique ID.
    """

    spells: dict[str,Spell] = {}

    with open(
        "data/rules/spells.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            spell = Spell(
                id=row["id"],
                name=row["name"],
                category=RuleCategory[row["category"]],
            )

            spells[spell.id] = spell

    return spells

def load_ability_tags() -> dict[str, AbilityTagEntity]:
    """
    Loads every ability tag from the database.

    Returns:
        A dictionary containing every AbilityTagEntity object,
        keyed by its unique ID.
    """

    ability_tags: dict[str,AbilityTagEntity] = {}

    with open(
        "data/rules/ability_tags.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            ability_tag = AbilityTagEntity(
                id=row["id"],
                name=row["name"],
            )

            ability_tags[ability_tag.id] = ability_tag

    return ability_tags

def load_ability_prerequisites() -> dict[str, AbilityPrerequisiteEntity]:
    """
    Loads every ability prerequisite from the database.

    Returns:
        A dictionary containing every AbilityPrerequisiteEntity object,
        keyed by its unique ID.
    """

    ability_prerequisites: dict[str, AbilityPrerequisiteEntity] = {}

    with open(
        "data/rules/ability_prerequisites.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            ability_prerequisite = AbilityPrerequisiteEntity(
                id=row["id"],
                name=row["name"],
            )

            ability_prerequisites[ability_prerequisite.id] = ability_prerequisite

    return ability_prerequisites                