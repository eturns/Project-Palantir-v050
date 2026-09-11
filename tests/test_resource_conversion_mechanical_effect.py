import pytest

from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from resource_conversion_mechanical_effect import (
    ResourceConversionMechanicalEffect,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_resource_conversion_mechanical_effect_stores_contract():
    effect = ResourceConversionMechanicalEffect(
        effect_type=(
            MechanicalEffectType.RESOURCE_CONVERSION
        ),
        target=(
            MechanicalEffectTarget.RESOURCE_USE
        ),
        source_id=(
            "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
        ),
        source_resource_type=ResourceType.WILL,
        target_resource_use=ResourceUse.TAKE_FATE,
    )

    assert effect.effect_type is (
        MechanicalEffectType.RESOURCE_CONVERSION
    )
    assert effect.target is (
        MechanicalEffectTarget.RESOURCE_USE
    )
    assert effect.source_resource_type is (
        ResourceType.WILL
    )
    assert effect.target_resource_use is (
        ResourceUse.TAKE_FATE
    )


def test_resource_conversion_mechanical_effect_rejects_wrong_type():
    with pytest.raises(
        ValueError,
        match="must use",
    ):
        ResourceConversionMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id=(
                "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
            ),
            source_resource_type=ResourceType.WILL,
            target_resource_use=(
                ResourceUse.TAKE_FATE
            ),
        )


def test_resource_conversion_mechanical_effect_rejects_wrong_target():
    with pytest.raises(
        ValueError,
        match="target must be RESOURCE_USE",
    ):
        ResourceConversionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .RESOURCE_CONVERSION
            ),
            target=(
                MechanicalEffectTarget.DUEL_ROLL
            ),
            source_id=(
                "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
            ),
            source_resource_type=ResourceType.WILL,
            target_resource_use=(
                ResourceUse.TAKE_FATE
            ),
        )


def test_resource_conversion_mechanical_effect_rejects_invalid_resource_type():
    with pytest.raises(
        TypeError,
        match="source_resource_type",
    ):
        ResourceConversionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .RESOURCE_CONVERSION
            ),
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id=(
                "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
            ),
            source_resource_type="WILL",
            target_resource_use=(
                ResourceUse.TAKE_FATE
            ),
        )


def test_resource_conversion_mechanical_effect_rejects_invalid_resource_use():
    with pytest.raises(
        TypeError,
        match="target_resource_use",
    ):
        ResourceConversionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .RESOURCE_CONVERSION
            ),
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id=(
                "HE_CANNOT_YET_TAKE_PHYSICAL_FORM"
            ),
            source_resource_type=ResourceType.WILL,
            target_resource_use="TAKE_FATE",
        )