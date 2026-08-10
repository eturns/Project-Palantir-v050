"""
Project Palantír
================

File:
    army_loader.py

Purpose:
    Loads factions and army lists.

Version:
    0.2.0-alpha

Created:
    DEV-026 – Army List Framework
"""

import csv

from faction import Faction
from army_list import ArmyList
from army_rule import ArmyRule
from loader_utils import validate_lookup
from ability_tag_entity import AbilityTagEntity


def load_factions() -> dict[str, Faction]:
    """
    Loads every MESBG faction.
    """

    factions: dict[str, Faction] = {}

    with open(
        "data/factions/factions.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            faction = Faction(
                id=row["id"],
                name=row["name"],
            )

            factions[faction.id] = faction

    return factions

def load_army_lists(
    factions: dict[str, Faction],
) -> dict[str, ArmyList]:
    """
    Loads every Army List.
    """

    army_lists: dict[str, ArmyList] = {}

    with open(
        "data/factions/army_lists.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            faction = factions[
                row["faction_id"]
            ]

            army_list = ArmyList(
                id=row["id"],
                name=row["name"],
                faction=faction,
            )

            army_lists[
                army_list.id
            ] = army_list

    return army_lists

def load_army_rules(
    army_lists: dict[str, ArmyList],
) -> dict[str, ArmyRule]:
    """
    Loads Army Rules for each Army List.
    """

    army_rules: dict[str, ArmyRule] = {}

    with open(
        "data/factions/army_rules.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:

            army_list = validate_lookup(
                row["army_list_id"],
                army_lists,
                "Army List",
                "army_rules.csv",
            )

            army_rule = ArmyRule(
                id=row["id"],
                name=row["name"],
            )

            army_rules[
                army_rule.id
            ] = army_rule

            army_list.army_rules.append(
                army_rule
            )

    return army_rules

def load_army_rule_tags(
    army_lists: dict[str, ArmyList],
    tags: dict[str, AbilityTagEntity],
) -> None:
    pass