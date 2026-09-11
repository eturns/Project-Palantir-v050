from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from post_combat_wound_effect import (
    PostCombatWoundEffect,
)


@dataclass(frozen=True)
class TriggeredMechanicalEffect(
    MechanicalEffect
):
    triggered_effect: PostCombatWoundEffect

    def __post_init__(self) -> None:
        super().__post_init__()

        if (
            self.effect_type
            is not MechanicalEffectType.TRIGGERED_EFFECT
        ):
            raise ValueError(
                "TriggeredMechanicalEffect must use "
                "MechanicalEffectType.TRIGGERED_EFFECT."
            )

        if (
            self.target
            is not MechanicalEffectTarget
            .POST_COMBAT_WOUND
        ):
            raise ValueError(
                "TriggeredMechanicalEffect target must "
                "be POST_COMBAT_WOUND."
            )

        if not isinstance(
            self.triggered_effect,
            PostCombatWoundEffect,
        ):
            raise TypeError(
                "triggered_effect must be a "
                "PostCombatWoundEffect."
            )