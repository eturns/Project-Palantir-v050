from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)
from relational_effect_condition import (
    RelationalEffectCondition,
)


@dataclass(frozen=True)
class MechanicalEffectDefinition:
    effect: MechanicalEffect
    applicability: MechanicalEffectApplicability
    relational_condition: (
        RelationalEffectCondition | None
    ) = None

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

        if (
            self.relational_condition is not None
            and not isinstance(
                self.relational_condition,
                RelationalEffectCondition,
            )
        ):
            raise TypeError(
                "relational_condition must be a "
                "RelationalEffectCondition or None."
            )