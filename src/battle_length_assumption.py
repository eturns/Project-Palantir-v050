from dataclasses import dataclass
from enum import Enum


class BattleEndType(Enum):
    FIXED_TURNS = "fixed_turns"
    ARMY_AT_QUARTER_STRENGTH = "army_at_quarter_strength"
    BROKEN_RANDOM_END = "broken_random_end"
    OBJECTIVE_COMPLETION = "objective_completion"
    EXTERNAL_TIME_LIMIT = "external_time_limit"


@dataclass(frozen=True)
class BattleLengthAssumption:
    assumed_turns: int
    end_type: BattleEndType

    def __post_init__(self) -> None:
        if self.assumed_turns < 1:
            raise ValueError(
                "Assumed battle length must be at least one turn."
            )

class BattleHorizon(Enum):
    SHORT = 6
    MEDIUM = 8
    LONG = 10


def battle_length_assumption_for_horizon(
    horizon: BattleHorizon,
    end_type: BattleEndType,
) -> BattleLengthAssumption:
    return BattleLengthAssumption(
        assumed_turns=horizon.value,
        end_type=end_type,
    )