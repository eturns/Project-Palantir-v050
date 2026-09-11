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
from post_combat_wound_effect import (
    PostCombatWoundEffect,
)
from triggered_effect_resolver import (
    resolved_triggered_effects,
)
from triggered_mechanical_effect import (
    TriggeredMechanicalEffect,
)


def make_definition(
    source_id: str,
    triggered_effect: PostCombatWoundEffect,
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=TriggeredMechanicalEffect(
            effect_type=(
                MechanicalEffectType.TRIGGERED_EFFECT
            ),
            target=(
                MechanicalEffectTarget.POST_COMBAT_WOUND
            ),
            source_id=source_id,
            triggered_effect=triggered_effect,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )


def test_resolved_triggered_effects_preserves_effects():
    first = PostCombatWoundEffect(
        additional_wound_on_roll=6,
    )
    second = PostCombatWoundEffect(
        additional_wound_on_roll=5,
    )

    result = resolved_triggered_effects(
        (
            make_definition(
                "FIRST",
                first,
            ),
            make_definition(
                "SECOND",
                second,
            ),
        )
    )

    assert result == (
        first,
        second,
    )


def test_resolved_triggered_effects_returns_empty_tuple():
    assert resolved_triggered_effects(
        ()
    ) == ()


def test_resolved_triggered_effects_rejects_wrong_effect_type():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.TRIGGERED_EFFECT
            ),
            target=(
                MechanicalEffectTarget.POST_COMBAT_WOUND
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
        resolved_triggered_effects(
            (definition,),
        )