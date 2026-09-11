import pytest

from mechanical_effect import MechanicalEffect
from mechanical_effect_applicability import (
    MechanicalEffectApplicability,
)
from mechanical_effect_applicability_type import (
    MechanicalEffectApplicabilityType,
)
from mechanical_effect_definition import (
    MechanicalEffectDefinition,
)
from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from resource_permission_effect_resolver import (
    resolved_resource_permissions,
)
from resource_permission_mechanical_effect import (
    ResourcePermissionMechanicalEffect,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def make_definition(
    source_id: str,
    resource_type: ResourceType,
    resource_use: ResourceUse,
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=ResourcePermissionMechanicalEffect(
            effect_type=(
                MechanicalEffectType.RESOURCE_PERMISSION
            ),
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id=source_id,
            resource_type=resource_type,
            resource_use=resource_use,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )


def test_resolved_resource_permissions_collects_unique_permissions():
    definitions = (
        make_definition(
            "FIRST",
            ResourceType.WILL,
            ResourceUse.BOOST_RESURRECTION,
        ),
        make_definition(
            "SECOND",
            ResourceType.WILL,
            ResourceUse.BOOST_RESURRECTION,
        ),
        make_definition(
            "THIRD",
            ResourceType.WILL,
            ResourceUse.TAKE_FATE,
        ),
    )

    assert resolved_resource_permissions(
        definitions,
    ) == {
        (
            ResourceType.WILL,
            ResourceUse.BOOST_RESURRECTION,
        ),
        (
            ResourceType.WILL,
            ResourceUse.TAKE_FATE,
        ),
    }


def test_resolved_resource_permissions_returns_empty_set():
    assert resolved_resource_permissions(
        ()
    ) == set()


def test_resolved_resource_permissions_rejects_wrong_effect_type():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.RESOURCE_PERMISSION
            ),
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id="BASE_EFFECT",
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )

    with pytest.raises(
        TypeError,
        match="All definitions must contain",
    ):
        resolved_resource_permissions(
            (definition,),
        )