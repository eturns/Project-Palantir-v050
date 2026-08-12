from dataclasses import dataclass


@dataclass(frozen=True)
class BattlefieldEffectsInputs:
    offence: float
    defence: float
    shooting: float
    courage: float
    command: float
    hero_hunting: float