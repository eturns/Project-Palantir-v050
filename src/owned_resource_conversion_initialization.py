from army import Army
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from resource_owner import ResourceOwner


def get_initial_owned_resource_conversions(
    army: Army,
) -> tuple[OwnedResourceConversion, ...]:
    conversions: list[OwnedResourceConversion] = []

    for entry in sorted(
        army.entries,
        key=lambda army_entry: army_entry.profile.id,
    ):
        for instance_index in range(
            1,
            entry.quantity + 1,
        ):
            owner = ResourceOwner(
                profile_id=entry.profile.id,
                instance_index=instance_index,
            )

            for conversion in (
                entry.profile.special_resource_conversions
            ):
                conversions.append(
                    OwnedResourceConversion(
                        owner=owner,
                        conversion=conversion,
                    )
                )

    return tuple(conversions)