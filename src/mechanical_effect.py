from dataclasses import dataclass

from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)


@dataclass(frozen=True)
class MechanicalEffect:
    effect_type: MechanicalEffectType
    target: MechanicalEffectTarget
    source_id: str

    def __post_init__(self) -> None:
        if not isinstance(
            self.effect_type,
            MechanicalEffectType,
        ):
            raise TypeError(
                "effect_type must be a "
                "MechanicalEffectType."
            )

        if not isinstance(
            self.target,
            MechanicalEffectTarget,
        ):
            raise TypeError(
                "target must be a "
                "MechanicalEffectTarget."
            )

        if not self.source_id:
            raise ValueError(
                "Mechanical effect source id "
                "must not be empty."
            )