import pytest

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
from roll_modifier_effect_resolver import (
    combined_roll_modifier_value,
)
from roll_modifier_mechanical_effect import (
    RollModifierMechanicalEffect,
)


def make_definition(
    source_id: str,
    value: int,
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=RollModifierMechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
            target=(
                MechanicalEffectTarget.TO_WOUND_ROLL
            ),
            source_id=source_id,
            value=value,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )


def test_combined_roll_modifier_value_sums_values():
    definitions = (
        make_definition(
            "FIRST",
            1,
        ),
        make_definition(
            "SECOND",
            -2,
        ),
        make_definition(
            "THIRD",
            3,
        ),
    )

    assert combined_roll_modifier_value(
        definitions,
    ) == 2


def test_combined_roll_modifier_value_returns_zero_for_empty_input():
    assert combined_roll_modifier_value(()) == 0


def test_combined_roll_modifier_value_rejects_base_effect():
    from mechanical_effect import MechanicalEffect

    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.ROLL_MODIFIER
            ),
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
        combined_roll_modifier_value(
            (definition,),
        )