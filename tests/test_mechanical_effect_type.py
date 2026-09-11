from mechanical_effect_type import MechanicalEffectType


def test_mechanical_effect_type_contains_expected_categories():
    assert set(MechanicalEffectType) == {
        MechanicalEffectType.ROLL_MODIFIER,
        MechanicalEffectType.REROLL,
        MechanicalEffectType.STRIKE_DAMAGE,
        MechanicalEffectType.RESOURCE_PERMISSION,
        MechanicalEffectType.RESOURCE_CONVERSION,
        MechanicalEffectType.POST_PREVENTION_EFFECT,
        MechanicalEffectType.TRIGGERED_EFFECT,
    }