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


def test_mechanical_effect_definition_stores_effect_and_applicability():
    effect = MechanicalEffect(
        effect_type=(
            MechanicalEffectType.STRIKE_DAMAGE
        ),
        target=(
            MechanicalEffectTarget.STRIKE_DAMAGE
        ),
        source_id="XBANE",
    )

    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.RACE
        ),
        value="ORC",
    )

    definition = MechanicalEffectDefinition(
        effect=effect,
        applicability=applicability,
    )

    assert definition.effect is effect
    assert definition.applicability is applicability


def test_mechanical_effect_definition_rejects_invalid_effect():
    applicability = MechanicalEffectApplicability(
        applicability_type=(
            MechanicalEffectApplicabilityType.ANY
        ),
    )

    with pytest.raises(
        TypeError,
        match="effect must be",
    ):
        MechanicalEffectDefinition(
            effect="not-an-effect",
            applicability=applicability,
        )


def test_mechanical_effect_definition_rejects_invalid_applicability():
    effect = MechanicalEffect(
        effect_type=(
            MechanicalEffectType.ROLL_MODIFIER
        ),
        target=(
            MechanicalEffectTarget.DUEL_ROLL
        ),
        source_id="TEST",
    )

    with pytest.raises(
        TypeError,
        match="applicability must be",
    ):
        MechanicalEffectDefinition(
            effect=effect,
            applicability="ANY",
        )