"""
Project Palantír

Ability Tags used for battlefield analysis.
"""

from enum import Enum


class AbilityTag(Enum):

    OFFENCE = "Offence"
    DEFENCE = "Defence"
    MOBILITY = "Mobility"
    MAGIC = "Magic"
    SHOOTING = "Shooting"
    COURAGE = "Courage"
    CONTROL = "Control"
    COMMAND = "Command"
    OBJECTIVE = "Objective"
    HERO_HUNTING = "Hero Hunting"