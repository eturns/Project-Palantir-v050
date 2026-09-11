from mechanical_effect_target import MechanicalEffectTarget


def test_mechanical_effect_target_contains_expected_operations():
    assert set(MechanicalEffectTarget) == {
        MechanicalEffectTarget.DUEL_ROLL,
        MechanicalEffectTarget.TO_WOUND_ROLL,
        MechanicalEffectTarget.STRIKE_DAMAGE,
        MechanicalEffectTarget.RESOURCE_USE,
        MechanicalEffectTarget.POST_PREVENTION,
        MechanicalEffectTarget.POST_COMBAT_WOUND,
    }