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
from reroll_effect_resolver import (
    resolved_reroll_scopes,
)
from reroll_mechanical_effect import (
    RerollMechanicalEffect,
)
from reroll_scope import RerollScope


def make_definition(
    source_id: str,
    scope: RerollScope,
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=RerollMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id=source_id,
            scope=scope,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )


def test_resolved_reroll_scopes_collects_unique_scopes():
    definitions = (
        make_definition(
            "FIRST",
            RerollScope.NATURAL_ONES,
        ),
        make_definition(
            "SECOND",
            RerollScope.FAILED,
        ),
        make_definition(
            "THIRD",
            RerollScope.NATURAL_ONES,
        ),
    )

    assert resolved_reroll_scopes(
        definitions,
    ) == {
        RerollScope.NATURAL_ONES,
        RerollScope.FAILED,
    }


def test_resolved_reroll_scopes_returns_empty_set():
    assert resolved_reroll_scopes(()) == set()


def test_resolved_reroll_scopes_rejects_wrong_effect_type():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
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
        resolved_reroll_scopes(
            (definition,),
        )