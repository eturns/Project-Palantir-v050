from dataclasses import dataclass
from enum import Enum


class StrikeDamageType(Enum):
    FIXED = "fixed"
    D3 = "d3"


@dataclass(frozen=True)
class StrikeDamage:
    damage_type: StrikeDamageType = StrikeDamageType.FIXED
    wounds_per_successful_strike: int = 1

    def __post_init__(self) -> None:
        if (
            self.damage_type == StrikeDamageType.FIXED
            and self.wounds_per_successful_strike < 1
        ):
            raise ValueError(
                "Wounds per successful strike must be at least 1."
            )