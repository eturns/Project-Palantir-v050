from dataclasses import dataclass
from enum import Enum


class ShatteredSpiritResult(Enum):
    NORMAL = "NORMAL"
    EMPOWERED = "EMPOWERED"
    OPPONENT_CONTROLLED = "OPPONENT_CONTROLLED"


@dataclass(frozen=True)
class ShatteredSpiritState:
    result: ShatteredSpiritResult = (
        ShatteredSpiritResult.NORMAL
    )

    @property
    def is_empowered(self) -> bool:
        return (
            self.result
            is ShatteredSpiritResult.EMPOWERED
        )

    @property
    def is_opponent_controlled(self) -> bool:
        return (
            self.result
            is ShatteredSpiritResult.OPPONENT_CONTROLLED
        )