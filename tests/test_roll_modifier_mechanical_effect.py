import pytest

from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from roll_modifier_mechanical_effect import (
    RollModifierMechanicalEffect,
)


def test_roll_modifier_mechanical_effect_stores_contract():
    effect = RollModifierMechanicalEffect(
        effect_type=(
            MechanicalEffectType.ROLL_MODIFIER
        ),
        target=(
            MechanicalEffectTarget.TO_WOUND_ROLL
        ),
        source_id="HATRED",
        value=1,
    )

    assert effect.effect_type is (
        MechanicalEffectType.ROLL_MODIFIER
    )
    assert effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )
    assert effect.source_id == "HATRED"
    assert effect.value == 1
    assert effect.ignored_on_natural_six is False


def test_roll_modifier_mechanical_effect_supports_duel_exception():
    effect = RollModifierMechanicalEffect(
        effect_type=(
            MechanicalEffectType.ROLL_MODIFIER
        ),
        target=MechanicalEffectTarget.DUEL_ROLL,
        source_id="WG_TWO_HANDED_WEAPON",
        value=-1,
        ignored_on_natural_six=True,
    )

    assert effect.value == -1
    assert effect.ignored_on_natural_six is True


def test_roll_modifier_mechanical_effect_rejects_wrong_type():
    with pytest.raises(
        ValueError,
        match="must use",
    ):
        RollModifierMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id="HATRED",
            value=1,
        )


def test_roll_modifier_mechanical_effect_rejects_unsupported_target():
    with pytest.raises(
        ValueError,
        match="supported roll target",
    ):
        RollModifierMechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
            ),
            source_id="HATRED",
            value=1,
        )


def test_roll_modifier_mechanical_effect_rejects_invalid_value():
    with pytest.raises(
        TypeError,
        match="value must be",
    ):
        RollModifierMechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id="HATRED",
            value="1",
        )


def test_roll_modifier_mechanical_effect_rejects_invalid_natural_six_flag():
    with pytest.raises(
        TypeError,
        match="ignored_on_natural_six",
    ):
        RollModifierMechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
            target=MechanicalEffectTarget.DUEL_ROLL,
            source_id="WG_TWO_HANDED_WEAPON",
            value=-1,
            ignored_on_natural_six="yes",
        )