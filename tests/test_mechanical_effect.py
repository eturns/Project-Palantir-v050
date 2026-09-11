import pytest

from mechanical_effect import MechanicalEffect
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)


def test_mechanical_effect_stores_core_contract():
    effect = MechanicalEffect(
        effect_type=(
            MechanicalEffectType.ROLL_MODIFIER
        ),
        target=(
            MechanicalEffectTarget.TO_WOUND_ROLL
        ),
        source_id="HATRED",
    )

    assert effect.effect_type is (
        MechanicalEffectType.ROLL_MODIFIER
    )
    assert effect.target is (
        MechanicalEffectTarget.TO_WOUND_ROLL
    )
    assert effect.source_id == "HATRED"


def test_mechanical_effect_rejects_invalid_effect_type():
    with pytest.raises(
        TypeError,
        match="effect_type must be",
    ):
        MechanicalEffect(
            effect_type="ROLL_MODIFIER",
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id="HATRED",
        )


def test_mechanical_effect_rejects_invalid_target():
    with pytest.raises(
        TypeError,
        match="target must be",
    ):
        MechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
            target="TO_WOUND_ROLL",
            source_id="HATRED",
        )


def test_mechanical_effect_rejects_empty_source_id():
    with pytest.raises(
        ValueError,
        match="source id",
    ):
        MechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id="",
        )