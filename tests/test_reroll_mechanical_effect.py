import pytest

from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from reroll_mechanical_effect import (
    RerollMechanicalEffect,
)
from reroll_scope import RerollScope


def test_reroll_mechanical_effect_stores_contract():
    effect = RerollMechanicalEffect(
        effect_type=MechanicalEffectType.REROLL,
        target=(
            MechanicalEffectTarget.TO_WOUND_ROLL
        ),
        source_id="BANE_OF_KINGS",
        scope=RerollScope.FAILED,
    )

    assert effect.effect_type is (
        MechanicalEffectType.REROLL
    )
    assert effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )
    assert effect.source_id == "BANE_OF_KINGS"
    assert effect.scope is RerollScope.FAILED


def test_reroll_mechanical_effect_rejects_wrong_type():
    with pytest.raises(
        ValueError,
        match="must use",
    ):
        RerollMechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id="BANE_OF_KINGS",
            scope=RerollScope.FAILED,
        )


def test_reroll_mechanical_effect_rejects_unsupported_target():
    with pytest.raises(
        ValueError,
        match="supported roll target",
    ):
        RerollMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
            ),
            source_id="BANE_OF_KINGS",
            scope=RerollScope.FAILED,
        )


def test_reroll_mechanical_effect_rejects_invalid_scope():
    with pytest.raises(
        TypeError,
        match="scope must be",
    ):
        RerollMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id="BANE_OF_KINGS",
            scope="FAILED",
        )