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
from post_prevention_effect import (
    PostPreventionEffect,
)
from post_prevention_effect_resolver import (
    resolved_post_prevention_effects,
)
from post_prevention_mechanical_effect import (
    PostPreventionMechanicalEffect,
)


def make_definition(
    source_id: str,
    post_prevention_effect: PostPreventionEffect,
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=PostPreventionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .POST_PREVENTION_EFFECT
            ),
            target=(
                MechanicalEffectTarget
                .POST_PREVENTION
            ),
            source_id=source_id,
            post_prevention_effect=(
                post_prevention_effect
            ),
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )


def test_resolved_post_prevention_effects_collects_unique_effects():
    definitions = (
        make_definition(
            "FIRST",
            PostPreventionEffect
            .REDUCE_WOUNDS_TO_ZERO,
        ),
        make_definition(
            "SECOND",
            PostPreventionEffect
            .REDUCE_WOUNDS_TO_ZERO,
        ),
    )

    assert resolved_post_prevention_effects(
        definitions,
    ) == {
        PostPreventionEffect
        .REDUCE_WOUNDS_TO_ZERO,
    }


def test_resolved_post_prevention_effects_returns_empty_set():
    assert resolved_post_prevention_effects(
        ()
    ) == set()


def test_resolved_post_prevention_effects_rejects_wrong_effect_type():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .POST_PREVENTION_EFFECT
            ),
            target=(
                MechanicalEffectTarget
                .POST_PREVENTION
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
        resolved_post_prevention_effects(
            (definition,),
        )