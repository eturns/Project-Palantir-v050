from army import Army
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from resource_owner import ResourceOwner
from special_rule_resource_conversions import (
    get_special_rule_resource_conversions,
)


def get_initial_owned_resource_conversions(
    army: Army,
) -> tuple[OwnedResourceConversion, ...]:
    conversions: list[OwnedResourceConversion] = []

    for entry in sorted(
        army.entries,
        key=lambda army_entry: army_entry.profile.id,
    ):
        profile = entry.profile

        special_rule_ids = tuple(
            assignment.rule.id
            for assignment in profile.special_rules
        )

        profile_conversions = (
            profile.special_resource_conversions
            + get_special_rule_resource_conversions(
                special_rule_ids=special_rule_ids,
            )
        )

        for instance_index in range(
            1,
            entry.quantity + 1,
        ):
            owner = ResourceOwner(
                profile_id=profile.id,
                instance_index=instance_index,
            )

            for conversion in profile_conversions:
                conversions.append(
                    OwnedResourceConversion(
                        owner=owner,
                        conversion=conversion,
                    )
                )

    return tuple(conversions)