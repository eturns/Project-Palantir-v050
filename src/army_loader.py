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
from profiles import Profile


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

def load_army_list_profiles(
    army_lists: dict[str, ArmyList],
    profiles_by_id: dict[str, Profile],
) -> None:
    """
    Loads canonical Profile membership for each ArmyList.

    A Profile may belong to more than one ArmyList.
    ArmyList.profiles contains references to the canonical
    Profile objects supplied in profiles_by_id.
    """

    seen_memberships: set[
        tuple[str, str]
    ] = set()

    with open(
        "data/factions/army_list_profiles.csv",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        for row in reader:
            army_list_id = row["army_list_id"]
            profile_id = row["profile_id"]

            membership = (
                army_list_id,
                profile_id,
            )

            if membership in seen_memberships:
                raise ValueError(
                    "Duplicate ArmyList profile membership: "
                    f"{army_list_id} / {profile_id}"
                )

            seen_memberships.add(
                membership
            )

            army_list = validate_lookup(
                army_list_id,
                army_lists,
                "Army List",
                "army_list_profiles.csv",
            )

            profile = validate_lookup(
                profile_id,
                profiles_by_id,
                "Profile",
                "army_list_profiles.csv",
            )

            army_list.profiles.append(
                profile
            )

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