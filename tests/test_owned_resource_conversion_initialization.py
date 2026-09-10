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

    for fielded_model in army.fielded_models():
        profile = (
            fielded_model
            .configured_profile
            .profile
        )

        owner = ResourceOwner(
            fielded_model_id=fielded_model.id,
        )

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

        for conversion in profile_conversions:
            conversions.append(
                OwnedResourceConversion(
                    owner=owner,
                    conversion=conversion,
                )
            )

    return tuple(conversions)