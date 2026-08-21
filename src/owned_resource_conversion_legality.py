from owned_resource_conversion import (
    OwnedResourceConversion,
)
from resource_conversion import ResourceConversion
from resource_owner import ResourceOwner


def is_owned_resource_conversion_permitted(
    owner: ResourceOwner,
    conversion: ResourceConversion,
    conversions: tuple[
        OwnedResourceConversion,
        ...,
    ],
) -> bool:
    return any(
        owned_conversion.owner == owner
        and owned_conversion.conversion == conversion
        for owned_conversion in conversions
    )