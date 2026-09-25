from army import Army
from owned_resource_conversion import (
    OwnedResourceConversion,
)
from resource_conversion_effect_resolver import (
    resolved_resource_conversions,
)
from resource_conversion_mechanical_effect import (
    ResourceConversionMechanicalEffect,
)
from resource_owner import ResourceOwner
from special_rule_mechanical_effect_definitions import (
    get_special_rule_mechanical_effect_definitions,
)


def get_initial_owned_resource_conversions(
    army: Army,
) -> tuple[OwnedResourceConversion, ...]:
    conversions: list[OwnedResourceConversion] = []

    for fielded_model in army.fielded_models():
        if fielded_model.configured_profile is None:
            continue

        profile = (
            fielded_model
            .configured_profile
            .profile
        )

        owner = ResourceOwner(
            fielded_model_id=fielded_model.id,
        )

        profile_conversions = (
            profile.special_resource_conversions
        )

        special_rule_definitions = (
            get_special_rule_mechanical_effect_definitions(
                fielded_model.configured_profile,
            )
        )

        conversion_definitions = tuple(
            definition
            for definition in special_rule_definitions
            if isinstance(
                definition.effect,
                ResourceConversionMechanicalEffect,
            )
        )

        generic_conversions = (
            resolved_resource_conversions(
                conversion_definitions,
            )
        )

        for conversion in (
            tuple(profile_conversions)
            + tuple(generic_conversions)
        ):
            conversions.append(
                OwnedResourceConversion(
                    owner=owner,
                    conversion=conversion,
                )
            )

    return tuple(conversions)