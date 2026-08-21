from resource_conversion import ResourceConversion
from resource_use import ResourceUse
from resource_use_permission import ResourceType


_HE_CANNOT_YET_TAKE_PHYSICAL_FORM = (
    "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
)


def get_special_rule_resource_conversions(
    special_rule_ids: tuple[str, ...],
) -> tuple[ResourceConversion, ...]:
    conversions: list[ResourceConversion] = []

    if _HE_CANNOT_YET_TAKE_PHYSICAL_FORM in special_rule_ids:
        conversions.append(
            ResourceConversion(
                source_resource_type=ResourceType.WILL,
                target_resource_use=ResourceUse.TAKE_FATE,
            )
        )

    return tuple(conversions)