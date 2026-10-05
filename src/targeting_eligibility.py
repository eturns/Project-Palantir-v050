from enum import Enum, auto

from shattered_spirit_state import (
    ShatteredSpiritState,
)


class TargetingSource(Enum):
    SHOOTING = auto()
    MAGICAL_POWER = auto()
    ENEMY_SPECIAL_RULE = auto()
    COMBAT_STRIKE = auto()
    IN_THE_WAY = auto()


def can_target_model(
    *,
    targeting_source: TargetingSource,
    shattered_spirit_state: ShatteredSpiritState | None = None,
    target_is_good: bool = False,
    source_is_good: bool = False,
) -> bool:
    if (
        shattered_spirit_state is None
        or not shattered_spirit_state.is_opponent_controlled
    ):
        return True

    if targeting_source in {
        TargetingSource.SHOOTING,
        TargetingSource.MAGICAL_POWER,
        TargetingSource.ENEMY_SPECIAL_RULE,
    }:
        return False

    if (
        target_is_good
        and source_is_good
        and targeting_source in {
            TargetingSource.COMBAT_STRIKE,
            TargetingSource.IN_THE_WAY,
        }
    ):
        return False

    return True