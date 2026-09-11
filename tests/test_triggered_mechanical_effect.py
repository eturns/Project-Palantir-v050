import pytest

from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from post_combat_wound_effect import (
    PostCombatWoundEffect,
)
from triggered_mechanical_effect import (
    TriggeredMechanicalEffect,
)


def test_triggered_mechanical_effect_stores_contract():
    effect = TriggeredMechanicalEffect(
        effect_type=(
            MechanicalEffectType.TRIGGERED_EFFECT
        ),
        target=(
            MechanicalEffectTarget.POST_COMBAT_WOUND
        ),
        source_id="VENOM",
        triggered_effect=PostCombatWoundEffect(
            additional_wound_on_roll=6,
        ),
    )

    assert effect.effect_type is (
        MechanicalEffectType.TRIGGERED_EFFECT
    )
    assert effect.target is (
        MechanicalEffectTarget.POST_COMBAT_WOUND
    )
    assert effect.source_id == "VENOM"
    assert (
        effect.triggered_effect.additional_wound_on_roll
        == 6
    )


def test_triggered_mechanical_effect_rejects_wrong_type():
    with pytest.raises(
        ValueError,
        match="must use",
    ):
        TriggeredMechanicalEffect(
            effect_type=MechanicalEffectType.REROLL,
            target=(
                MechanicalEffectTarget.POST_COMBAT_WOUND
            ),
            source_id="VENOM",
            triggered_effect=PostCombatWoundEffect(
                additional_wound_on_roll=6,
            ),
        )


def test_triggered_mechanical_effect_rejects_wrong_target():
    with pytest.raises(
        ValueError,
        match="target must be POST_COMBAT_WOUND",
    ):
        TriggeredMechanicalEffect(
            effect_type=(
                MechanicalEffectType.TRIGGERED_EFFECT
            ),
            target=(
                MechanicalEffectTarget.DUEL_ROLL
            ),
            source_id="VENOM",
            triggered_effect=PostCombatWoundEffect(
                additional_wound_on_roll=6,
            ),
        )


def test_triggered_mechanical_effect_rejects_invalid_effect():
    with pytest.raises(
        TypeError,
        match="triggered_effect must be",
    ):
        TriggeredMechanicalEffect(
            effect_type=(
                MechanicalEffectType.TRIGGERED_EFFECT
            ),
            target=(
                MechanicalEffectTarget.POST_COMBAT_WOUND
            ),
            source_id="VENOM",
            triggered_effect="6",
        )