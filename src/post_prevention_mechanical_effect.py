from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from post_prevention_effect import (
    PostPreventionEffect,
)


@dataclass(frozen=True)
class PostPreventionMechanicalEffect(
    MechanicalEffect
):
    post_prevention_effect: PostPreventionEffect

    def __post_init__(self) -> None:
        super().__post_init__()

        if (
            self.effect_type
            is not MechanicalEffectType
            .POST_PREVENTION_EFFECT
        ):
            raise ValueError(
                "PostPreventionMechanicalEffect "
                "must use "
                "MechanicalEffectType."
                "POST_PREVENTION_EFFECT."
            )

        if (
            self.target
            is not MechanicalEffectTarget
            .POST_PREVENTION
        ):
            raise ValueError(
                "PostPreventionMechanicalEffect "
                "target must be POST_PREVENTION."
            )

        if not isinstance(
            self.post_prevention_effect,
            PostPreventionEffect,
        ):
            raise TypeError(
                "post_prevention_effect must be "
                "a PostPreventionEffect."
            )