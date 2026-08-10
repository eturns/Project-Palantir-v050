from dataclasses import dataclass


@dataclass(frozen=True)
class DuelReroll:
    available: bool = False