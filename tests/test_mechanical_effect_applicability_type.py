from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)


def test_mechanical_effect_applicability_type_contains_expected_values():
    assert set(MechanicalEffectApplicabilityType) == {
        MechanicalEffectApplicabilityType.ANY,
        MechanicalEffectApplicabilityType.RACE,
        MechanicalEffectApplicabilityType.KEYWORD,
        MechanicalEffectApplicabilityType.MODEL_TYPE,
        MechanicalEffectApplicabilityType.HEROIC_STATUS,
        MechanicalEffectApplicabilityType.FIELDED_MODEL_ID,
    }