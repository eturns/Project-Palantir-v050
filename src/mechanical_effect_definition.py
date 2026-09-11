from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)


@dataclass(frozen=True)
class MechanicalEffectDefinition:
    effect: MechanicalEffect
    applicability: MechanicalEffectApplicability

    def __post_init__(self) -> None:
        if not isinstance(
            self.effect,
            MechanicalEffect,
        ):
            raise TypeError(
                "effect must be a MechanicalEffect."
            )

        if not isinstance(
            self.applicability,
            MechanicalEffectApplicability,
        ):
            raise TypeError(
                "applicability must be a "
                "MechanicalEffectApplicability."
            )