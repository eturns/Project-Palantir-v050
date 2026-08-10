"""
Project Palantír
================

File:
    relationship_loader.py

Purpose:
    Loads relationships between Profiles and their game entities.

Version:
    0.1.0-alpha

Authors:
    Edward Turns (Project Lead)
    OpenAI ChatGPT (Technical Lead)

Created:
    DEV-012 – Relationship Loader
"""

# ============================================================================
# Imports
# ============================================================================

import csv

from profiles import Profile
from special_rule import SpecialRule
from heroic_action import HeroicAction
from spell import Spell
from ability_tag_entity import AbilityTagEntity
from ability_prerequisite_entity import AbilityPrerequisiteEntity
from ability_tag_assignment import AbilityTagAssignment
from profile_spell_assignment import (
    ProfileSpellAssignment,
)
from loader_utils import validate_lookup
from army_rule import ArmyRule
from profile_special_rule_assignment import (
    ProfileSpecialRuleAssignment,
)

# ============================================================================
# Functions
# ============================================================================

def load_profile_special_rules(
    profiles: dict[str, Profile],
    special_rules: dict[str, SpecialRule],
) -> None:
    """
    Loads special rule relationships for every Profile.
    """

    with open(
        "data/profiles/profile_special_rules.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            profile = validate_lookup(
                row["profile_id"],
                profiles,
                "Profile",
                "profile_special_rules.csv",
            )

            rule = validate_lookup(
                row["rule_id"],
                special_rules,
                "Special Rule",
                "profile_special_rules.csv",
            )

            parameter_text = (row.get("parameter") or "").strip()

            parameter = (
                int(parameter_text)
                if parameter_text
                else None
            )

            profile.special_rules.append(
                ProfileSpecialRuleAssignment(
                rule=rule,
                parameter=parameter,
                )
            )


def load_profile_heroic_actions(
    profiles: dict[str, Profile],
    heroic_actions: dict[str, HeroicAction],
) -> None:
    """
    Loads heroic action relationships for every Profile.
    """

    with open(
        "data/profiles/profile_heroic_actions.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            profile = validate_lookup(
                row["profile_id"],
                profiles,
                "Profile",
                "profile_heroic_actions.csv",
            )

            heroic_action = validate_lookup(
                row["heroic_action_id"],
                heroic_actions,
                "Heroic Action",
                "profile_heroic_actions.csv",
            )

            profile.heroic_actions.append(heroic_action)


def load_profile_spells(
    profiles: dict[str, Profile],
    spells: dict[str, Spell],
) -> None:
    """
    Loads spell relationships for every Profile.
    """

    with open(
        "data/profiles/profile_spells.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            profile = validate_lookup(
                row["profile_id"],
                profiles,
                "Profile",
                "profile_spells.csv",
            )

            spell = validate_lookup(
                row["spell_id"],
                spells,
                "Spell",
                "profile_spells.csv",
            )

            profile.spells.append(
                ProfileSpellAssignment(
                    spell=spell,
                    cast_value=int(
                        row["cast_value"],
                    ),
                )
            )

def load_heroic_action_tags(
    heroic_actions: dict[str, HeroicAction],
    ability_tags: dict[str, AbilityTagEntity],
) -> None:
    """
    Loads Ability Tag relationships for every Heroic Action.
    """

    with open(
        "data/rules/heroic_action_tags.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            heroic_action = validate_lookup(
                row["heroic_action_id"],
                heroic_actions,
                "Heroic Action",
                "heroic_action_tags.csv",
            )

            ability_tag = validate_lookup(
                row["ability_tag_id"],
                ability_tags,
                "Ability Tag",
                "heroic_action_tags.csv",
            )

            heroic_action.ability_tags.append(
                AbilityTagAssignment(
                    tag=ability_tag,
                    weight=float(
                        row["weight"],
                    ),
                )
            )

def load_special_rule_tags(
    special_rules: dict[str, SpecialRule],
    ability_tags: dict[str, AbilityTagEntity],
) -> None:
    """
    Loads Ability Tag relationships for every Special rule.
    """

    with open(
        "data/rules/special_rule_tags.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            rule = validate_lookup(
                row["special_rule_id"],
                special_rules,
                "Special Rule",
                "special_rule_tags.csv",
            )

            ability_tag = validate_lookup(
                row["ability_tag_id"],
                ability_tags,
                "Ability Tag",
                "special_rule_tags.csv",
            )

            rule.ability_tags.append(
                AbilityTagAssignment(
                    tag=ability_tag,
                    weight=float(
                        row["weight"],
                    ),
                )
            )

def load_spell_tags(
    spells: dict[str, Spell],
    ability_tags: dict[str, AbilityTagEntity],
) -> None:
    """
    Loads Ability Tag relationships for every Sppell.
    """

    with open(
        "data/rules/spell_tags.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            spell = validate_lookup(
                row["spell_id"],
                spells,
                "Spell",
                "spell_tags.csv",
            )

            ability_tag = validate_lookup(
                row["ability_tag_id"],
                ability_tags,
                "Ability Tag",
                "spell_tags.csv",
            )

            spell.ability_tags.append(
                AbilityTagAssignment(
                    tag=ability_tag,
                    weight=float(
                        row["weight"],
                    ),
                )
            )


def load_heroic_action_prerequisites(
    heroic_actions: dict[str, HeroicAction],
    ability_prerequisites: dict[str, AbilityPrerequisiteEntity],
) -> None:
    """
    Loads Ability Prerequisite relationships for every Heroic Action.
    """

    with open(
        "data/rules/heroic_action_prerequisites.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            heroic_action = validate_lookup(
                row["heroic_action_id"],
                heroic_actions,
                "Heroic Action",
                "heroic_action_prerequisites.csv",
            )

            prerequisite = validate_lookup(
                row["ability_prerequisite_id"],
                ability_prerequisites,
                "Ability Prerequisite",
                "heroic_action_prerequisites.csv",
            )

            heroic_action.prerequisites.append(prerequisite)

def load_special_rule_prerequisites(
    special_rules: dict[str, SpecialRule],
    ability_prerequisites: dict[str, AbilityPrerequisiteEntity],
) -> None:
    """
    Loads Ability Prerequisite relationships for every Special Rule.
    """

    with open(
        "data/rules/special_rule_prerequisites.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            special_rule = validate_lookup(
                row["special_rule_id"],
                special_rules,
                "Special Rule",
                "special_rule_prerequisites.csv",
            )

            prerequisite = validate_lookup(
                row["ability_prerequisite_id"],
                ability_prerequisites,
                "Ability Prerequisite",
                "special_rule_prerequisites.csv",
            )

            special_rule.prerequisites.append(prerequisite)

def load_spell_prerequisites(
    spells: dict[str, Spell],
    ability_prerequisites: dict[str, AbilityPrerequisiteEntity],
) -> None:
    """
    Loads Ability Prerequisite relationships for every Spell.
    """

    with open(
        "data/rules/spell_prerequisites.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            spell = validate_lookup(
                row["spell_id"],
                spells,
                "Spell",
                "spell_prerequisites.csv",
            )

            prerequisite = validate_lookup(
                row["ability_prerequisite_id"],
                ability_prerequisites,
                "Ability Prerequisite",
                "spell_prerequisites.csv",
            )

            spell.prerequisites.append(prerequisite)

def load_army_rule_tags(
    army_rules: dict[str, ArmyRule],
    ability_tags: dict[str, AbilityTagEntity],
) -> None:
    """
    Loads Ability Tag relationships for every Army Rule.
    """

    with open(
        "data/factions/army_rule_tags.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            army_rule = validate_lookup(
                row["army_rule_id"],
                army_rules,
                "Army Rule",
                "army_rule_tags.csv",
            )

            ability_tag = validate_lookup(
                row["tag_id"],
                ability_tags,
                "Ability Tag",
                "army_rule_tags.csv",
            )

            army_rule.ability_tags.append(
                AbilityTagAssignment(
                    tag=ability_tag,
                    weight=float(
                        row["weight"],
                    ),
                )
            )