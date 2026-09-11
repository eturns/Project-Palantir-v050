import pytest

from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from resource_permission_mechanical_effect import (
    ResourcePermissionMechanicalEffect,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def test_resource_permission_mechanical_effect_stores_contract():
    effect = ResourcePermissionMechanicalEffect(
        effect_type=(
            MechanicalEffectType.RESOURCE_PERMISSION
        ),
        target=(
            MechanicalEffectTarget.RESOURCE_USE
        ),
        source_id="UNHOLY_RESURRECTION",
        resource_type=ResourceType.WILL,
        resource_use=(
            ResourceUse.BOOST_RESURRECTION
        ),
    )

    assert effect.effect_type is (
        MechanicalEffectType.RESOURCE_PERMISSION
    )
    assert effect.target is (
        MechanicalEffectTarget.RESOURCE_USE
    )
    assert effect.source_id == (
        "UNHOLY_RESURRECTION"
    )
    assert effect.resource_type is ResourceType.WILL
    assert effect.resource_use is (
        ResourceUse.BOOST_RESURRECTION
    )


def test_resource_permission_mechanical_effect_rejects_wrong_type():
    with pytest.raises(
        ValueError,
        match="must use",
    ):
        ResourcePermissionMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id="UNHOLY_RESURRECTION",
            resource_type=ResourceType.WILL,
            resource_use=(
                ResourceUse.BOOST_RESURRECTION
            ),
        )


def test_resource_permission_mechanical_effect_rejects_wrong_target():
    with pytest.raises(
        ValueError,
        match="target must be RESOURCE_USE",
    ):
        ResourcePermissionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .RESOURCE_PERMISSION
            ),
            target=(
                MechanicalEffectTarget.DUEL_ROLL
            ),
            source_id="UNHOLY_RESURRECTION",
            resource_type=ResourceType.WILL,
            resource_use=(
                ResourceUse.BOOST_RESURRECTION
            ),
        )


def test_resource_permission_mechanical_effect_rejects_invalid_resource_type():
    with pytest.raises(
        TypeError,
        match="resource_type must be",
    ):
        ResourcePermissionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .RESOURCE_PERMISSION
            ),
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id="UNHOLY_RESURRECTION",
            resource_type="WILL",
            resource_use=(
                ResourceUse.BOOST_RESURRECTION
            ),
        )


def test_resource_permission_mechanical_effect_rejects_invalid_resource_use():
    with pytest.raises(
        TypeError,
        match="resource_use must be",
    ):
        ResourcePermissionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .RESOURCE_PERMISSION
            ),
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id="UNHOLY_RESURRECTION",
            resource_type=ResourceType.WILL,
            resource_use="BOOST_RESURRECTION",
        )