from dataclasses import dataclass

from mechanical_effect import MechanicalEffect
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType


@dataclass(frozen=True)
class ResourceConversionMechanicalEffect(
    MechanicalEffect
):
    source_resource_type: ResourceType
    target_resource_use: ResourceUse

    def __post_init__(self) -> None:
        super().__post_init__()

        if (
            self.effect_type
            is not MechanicalEffectType.RESOURCE_CONVERSION
        ):
            raise ValueError(
                "ResourceConversionMechanicalEffect "
                "must use "
                "MechanicalEffectType.RESOURCE_CONVERSION."
            )

        if (
            self.target
            is not MechanicalEffectTarget.RESOURCE_USE
        ):
            raise ValueError(
                "ResourceConversionMechanicalEffect "
                "target must be RESOURCE_USE."
            )

        if not isinstance(
            self.source_resource_type,
            ResourceType,
        ):
            raise TypeError(
                "source_resource_type must be "
                "a ResourceType."
            )

        if not isinstance(
            self.target_resource_use,
            ResourceUse,
        ):
            raise TypeError(
                "target_resource_use must be "
                "a ResourceUse."
            )