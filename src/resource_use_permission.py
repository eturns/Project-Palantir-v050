from enum import Enum

from resource_use import ResourceUse


class ResourceType(Enum):
    MIGHT = "might"
    WILL = "will"
    FATE = "fate"


_DEFAULT_PERMITTED_USES = {
    ResourceType.MIGHT: {
        ResourceUse.MODIFY_DUEL,
        ResourceUse.MODIFY_WOUND,
    },
    ResourceType.WILL: {
        ResourceUse.CAST_SPELL,
        ResourceUse.RESIST_MAGIC,
    },
    ResourceType.FATE: {
        ResourceUse.TAKE_FATE,
    },
}


def is_resource_use_permitted(
    resource_type: ResourceType,
    resource_use: ResourceUse,
) -> bool:
    return (
        resource_use
        in _DEFAULT_PERMITTED_USES[resource_type]
    )