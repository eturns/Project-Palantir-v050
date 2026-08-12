from dataclasses import dataclass


@dataclass(frozen=True)
class ArmyResourceState:
    might: int
    will: int
    fate: int