from fielded_model import FieldedModel
from mechanical_effect_applicability_matcher import (
    mechanical_effect_applies_to_fielded_model,
)
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from relational_effect_condition_matcher import (
    relational_effect_condition_matches,
)
from profiles import Profile

def mechanical_effect_definition_applies_to_fielded_model(
    definition: MechanicalEffectDefinition,
    fielded_model: FieldedModel,
    related_models: tuple[FieldedModel, ...] = (),
    related_profiles: tuple[Profile, ...] = (),
) -> bool:
    if not mechanical_effect_applies_to_fielded_model(
        definition.applicability,
        fielded_model,
    ):
        return False

    if definition.relational_condition is None:
        return True

    candidate_profiles = (
        related_profiles
        + tuple(
            related_model.configured_profile.profile
            for related_model in related_models
        )
    )

    return any(
        relational_effect_condition_matches(
            definition.relational_condition,
            subject=(
                fielded_model
                .configured_profile
                .profile
            ),
            related_model=related_profile,
        )
        for related_profile in candidate_profiles
    )