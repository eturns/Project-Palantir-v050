from dataclasses import dataclass


@dataclass(frozen=True)
class MorgulBladeState:
    used: bool = False
    active_this_combat: bool = False