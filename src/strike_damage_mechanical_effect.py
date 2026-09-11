from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from strike_damage import StrikeDamage


@dataclass(frozen=True)
class StrikeDamageMechanicalEffect(
    MechanicalEffect
):
    strike_damage: StrikeDamage

    def __post_init__(self) -> None:
        super().__post_init__()

        if (
            self.effect_type
            is not MechanicalEffectType.STRIKE_DAMAGE
        ):
            raise ValueError(
                "StrikeDamageMechanicalEffect must use "
                "MechanicalEffectType.STRIKE_DAMAGE."
            )

        if (
            self.target
            is not MechanicalEffectTarget.STRIKE_DAMAGE
        ):
            raise ValueError(
                "StrikeDamageMechanicalEffect target "
                "must be STRIKE_DAMAGE."
            )

        if not isinstance(
            self.strike_damage,
            StrikeDamage,
        ):
            raise TypeError(
                "strike_damage must be a StrikeDamage."
            )