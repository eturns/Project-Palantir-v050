from dataclasses import dataclass


@dataclass
class ArmyRuleMetrics:
    """
    Battlefield metric contribution from a single Army Rule.
    """

    offence: float = 0.0
    defence: float = 0.0
    mobility: float = 0.0
    magic: float = 0.0
    shooting: float = 0.0
    courage: float = 0.0
    control: float = 0.0
    command: float = 0.0
    objective: float = 0.0
    hero_hunting: float = 0.0