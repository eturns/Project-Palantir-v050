from dataclasses import dataclass
from enum import Enum


class RelationalEffectConditionType(Enum):
    FRIENDLY_MODEL_DIFFERENT_RACE = (
        "FRIENDLY_MODEL_DIFFERENT_RACE"
    )


@dataclass(frozen=True)
class RelationalEffectCondition:
    condition_type: RelationalEffectConditionType

    def __post_init__(self) -> None:
        if not isinstance(
            self.condition_type,
            RelationalEffectConditionType,
        ):
            raise TypeError(
                "condition_type must be a "
                "RelationalEffectConditionType."
            )