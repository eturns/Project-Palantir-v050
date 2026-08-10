from enum import Enum


class RuleCategory(Enum):
    """
    Categories used to group Special Rules,
    Heroic Actions and Spells.
    """

    OFFENCE = "Offence"
    DEFENCE = "Defence"
    MOBILITY = "Mobility"
    MAGIC = "Magic"
    COURAGE = "Courage"
    COMMAND = "Command"
    MONSTER = "Monster"
    SHOOTING = "Shooting"
    MOVEMENT = "Movement"
    SPECIAL = "Special"