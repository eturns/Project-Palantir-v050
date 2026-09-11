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
class ResourcePermissionMechanicalEffect(
    MechanicalEffect
):
    resource_type: ResourceType
    resource_use: ResourceUse

    def __post_init__(self) -> None:
        super().__post_init__()

        if (
            self.effect_type
            is not MechanicalEffectType.RESOURCE_PERMISSION
        ):
            raise ValueError(
                "ResourcePermissionMechanicalEffect "
                "must use "
                "MechanicalEffectType.RESOURCE_PERMISSION."
            )

        if (
            self.target
            is not MechanicalEffectTarget.RESOURCE_USE
        ):
            raise ValueError(
                "ResourcePermissionMechanicalEffect "
                "target must be RESOURCE_USE."
            )

        if not isinstance(
            self.resource_type,
            ResourceType,
        ):
            raise TypeError(
                "resource_type must be a ResourceType."
            )

        if not isinstance(
            self.resource_use,
            ResourceUse,
        ):
            raise TypeError(
                "resource_use must be a ResourceUse."
            )