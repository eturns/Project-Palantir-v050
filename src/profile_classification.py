from enum import Enum


class HeroicStatus(Enum):
    HERO = "HERO"
    WARRIOR = "WARRIOR"


class ModelType(Enum):
    INFANTRY = "INFANTRY"
    CAVALRY = "CAVALRY"
    BEAST = "BEAST"
    MONSTER = "MONSTER"