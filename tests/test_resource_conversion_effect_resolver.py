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
from resource_conversion import ResourceConversion
from resource_conversion_effect_resolver import (
    resolved_resource_conversions,
)
from resource_conversion_mechanical_effect import (
    ResourceConversionMechanicalEffect,
)
from resource_use import ResourceUse
from resource_use_permission import ResourceType


def make_definition(
    source_id: str,
    source_resource_type: ResourceType,
    target_resource_use: ResourceUse,
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=ResourceConversionMechanicalEffect(
            effect_type=(
                MechanicalEffectType.RESOURCE_CONVERSION
            ),
            target=(
                MechanicalEffectTarget.RESOURCE_USE
            ),
            source_id=source_id,
            source_resource_type=source_resource_type,
            target_resource_use=target_resource_use,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )


def test_resolved_resource_conversions_collects_unique_conversions():
    definitions = (
        make_definition(
            "FIRST",
            ResourceType.WILL,
            ResourceUse.TAKE_FATE,
        ),
        make_definition(
            "SECOND",
            ResourceType.WILL,
            ResourceUse.TAKE_FATE,
        ),
    )

    assert resolved_resource_conversions(
        definitions,
    ) == {
        ResourceConversion(
            source_resource_type=ResourceType.WILL,
            target_resource_use=ResourceUse.TAKE_FATE,
        ),
    }


def test_resolved_resource_conversions_returns_empty_set():
    assert resolved_resource_conversions(
        ()
    ) == set()


def test_resolved_resource_conversions_rejects_wrong_effect_type():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.RESOURCE_CONVERSION
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
        resolved_resource_conversions(
            (definition,),
        )