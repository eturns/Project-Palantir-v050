from dataclasses import dataclass


@dataclass(frozen=True)
class WoundReroll:
    reroll_failed: bool = False
    reroll_natural_ones: bool = False