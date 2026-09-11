import pytest

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
from strike_damage_mechanical_effect import (
    StrikeDamageMechanicalEffect,
)


def test_strike_damage_mechanical_effect_stores_fixed_damage():
    effect = StrikeDamageMechanicalEffect(
        effect_type=(
            MechanicalEffectType.STRIKE_DAMAGE
        ),
        target=(
            MechanicalEffectTarget.STRIKE_DAMAGE
        ),
        source_id="MIGHTY_BLOW",
        strike_damage=StrikeDamage(
            wounds_per_successful_strike=2,
        ),
    )

    assert effect.effect_type is (
        MechanicalEffectType.STRIKE_DAMAGE
    )
    assert effect.target is (
        MechanicalEffectTarget.STRIKE_DAMAGE
    )
    assert (
        effect.strike_damage
        .wounds_per_successful_strike
        == 2
    )


def test_strike_damage_mechanical_effect_supports_d3():
    effect = StrikeDamageMechanicalEffect(
        effect_type=(
            MechanicalEffectType.STRIKE_DAMAGE
        ),
        target=(
            MechanicalEffectTarget.STRIKE_DAMAGE
        ),
        source_id="XBANE",
        strike_damage=StrikeDamage(
            damage_type=StrikeDamageType.D3,
        ),
    )

    assert (
        effect.strike_damage.damage_type
        is StrikeDamageType.D3
    )


def test_strike_damage_mechanical_effect_rejects_wrong_type():
    with pytest.raises(
        ValueError,
        match="must use",
    ):
        StrikeDamageMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
            ),
            source_id="MIGHTY_BLOW",
            strike_damage=StrikeDamage(
                wounds_per_successful_strike=2,
            ),
        )


def test_strike_damage_mechanical_effect_rejects_wrong_target():
    with pytest.raises(
        ValueError,
        match="target must be STRIKE_DAMAGE",
    ):
        StrikeDamageMechanicalEffect(
            effect_type=(
                MechanicalEffectType.STRIKE_DAMAGE
            ),
            target=(
                MechanicalEffectTarget.DUEL_ROLL
            ),
            source_id="MIGHTY_BLOW",
            strike_damage=StrikeDamage(
                wounds_per_successful_strike=2,
            ),
        )


def test_strike_damage_mechanical_effect_rejects_invalid_damage():
    with pytest.raises(
        TypeError,
        match="strike_damage must be",
    ):
        StrikeDamageMechanicalEffect(
            effect_type=(
                MechanicalEffectType.STRIKE_DAMAGE
            ),
            target=(
                MechanicalEffectTarget.STRIKE_DAMAGE
            ),
            source_id="MIGHTY_BLOW",
            strike_damage="2",
        )