from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from reroll_scope import RerollScope


@dataclass(frozen=True)
class RerollMechanicalEffect(
    MechanicalEffect
):
    scope: RerollScope

    def __post_init__(self) -> None:
        super().__post_init__()

        if (
            self.effect_type
            is not MechanicalEffectType.REROLL
        ):
            raise ValueError(
                "RerollMechanicalEffect must use "
                "MechanicalEffectType.REROLL."
            )

        if self.target not in (
            MechanicalEffectTarget.DUEL_ROLL,
            MechanicalEffectTarget.TO_WOUND_ROLL,
        ):
            raise ValueError(
                "RerollMechanicalEffect target must be "
                "a supported roll target."
            )

        if not isinstance(
            self.scope,
            RerollScope,
        ):
            raise TypeError(
                "scope must be a RerollScope."
            )