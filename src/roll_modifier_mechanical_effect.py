from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)


@dataclass(frozen=True)
class RollModifierMechanicalEffect(
    MechanicalEffect
):
    value: int
    ignored_on_natural_six: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()

        if (
            self.effect_type
            is not MechanicalEffectType.ROLL_MODIFIER
        ):
            raise ValueError(
                "RollModifierMechanicalEffect must use "
                "MechanicalEffectType.ROLL_MODIFIER."
            )

        if self.target not in (
            MechanicalEffectTarget.DUEL_ROLL,
            MechanicalEffectTarget.TO_WOUND_ROLL,
        ):
            raise ValueError(
                "RollModifierMechanicalEffect target must "
                "be a supported roll target."
            )

        if not isinstance(
            self.value,
            int,
        ):
            raise TypeError(
                "value must be an int."
            )

        if not isinstance(
            self.ignored_on_natural_six,
            bool,
        ):
            raise TypeError(
                "ignored_on_natural_six must be a bool."
            )