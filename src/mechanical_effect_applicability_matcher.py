from fielded_model import FieldedModel
from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)


def mechanical_effect_applies_to_fielded_model(
    applicability: MechanicalEffectApplicability,
    fielded_model: FieldedModel,
) -> bool:
    applicability_type = (
        applicability.applicability_type
    )
    value = applicability.value

    if (
        applicability_type
        is MechanicalEffectApplicabilityType.ANY
    ):
        return True

    if (
        applicability_type
        is MechanicalEffectApplicabilityType.RACE
    ):
        return (
            value
            in fielded_model
            .configured_profile
            .profile
            .races
        )

    if (
        applicability_type
        is MechanicalEffectApplicabilityType.KEYWORD
    ):
        return (
            value
            in fielded_model
            .configured_profile
            .profile
            .keywords
        )

    if (
        applicability_type
        is MechanicalEffectApplicabilityType.MODEL_TYPE
    ):
        return (
            value
            in fielded_model
            .configured_profile
            .effective_model_types
        )

    if (
        applicability_type
        is MechanicalEffectApplicabilityType
        .HEROIC_STATUS
    ):
        return (
            fielded_model
            .configured_profile
            .profile
            .heroic_status
            is value
        )

    if (
        applicability_type
        is MechanicalEffectApplicabilityType
        .FIELDED_MODEL_ID
    ):
        return fielded_model.id == value

    raise ValueError(
        "Unsupported mechanical effect "
        "applicability type."
    )