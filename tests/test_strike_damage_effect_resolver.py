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
from strike_damage import (
    StrikeDamage,
    StrikeDamageType,
)
from strike_damage_effect_resolver import (
    resolved_strike_damage_effects,
)
from strike_damage_mechanical_effect import (
    StrikeDamageMechanicalEffect,
)


def make_definition(
    source_id: str,
    strike_damage: StrikeDamage,
) -> MechanicalEffectDefinition:
    return MechanicalEffectDefinition(
        effect=StrikeDamageMechanicalEffect(
            effect_type=(
                MechanicalEffectType.STRIKE_DAMAGE
            ),
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
            ),
            source_id=source_id,
            strike_damage=strike_damage,
        ),
        applicability=MechanicalEffectApplicability(
            applicability_type=(
                MechanicalEffectApplicabilityType.ANY
            ),
        ),
    )


def test_resolved_strike_damage_effects_preserves_damage_instructions():
    definitions = (
        make_definition(
            "MIGHTY_BLOW",
            StrikeDamage(
                wounds_per_successful_strike=2,
            ),
        ),
        make_definition(
            "XBANE",
            StrikeDamage(
                damage_type=StrikeDamageType.D3,
            ),
        ),
    )

    result = resolved_strike_damage_effects(
        definitions,
    )

    assert len(result) == 2

    assert (
        result[0].wounds_per_successful_strike
        == 2
    )

    assert (
        result[1].damage_type
        is StrikeDamageType.D3
    )


def test_resolved_strike_damage_effects_preserves_order():
    first = StrikeDamage(
        wounds_per_successful_strike=2,
    )
    second = StrikeDamage(
        damage_type=StrikeDamageType.D3,
    )

    result = resolved_strike_damage_effects(
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


def test_resolved_strike_damage_effects_returns_empty_tuple():
    assert resolved_strike_damage_effects(
        ()
    ) == ()


def test_resolved_strike_damage_effects_rejects_wrong_effect_type():
    definition = MechanicalEffectDefinition(
        effect=MechanicalEffect(
            effect_type=(
                MechanicalEffectType.STRIKE_DAMAGE
            ),
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
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
        resolved_strike_damage_effects(
            (definition,),
        )