import pytest

from mechanical_effect_target import (
    MechanicalEffectTarget,
)
from mechanical_effect_type import (
    MechanicalEffectType,
)
from post_prevention_effect import (
    PostPreventionEffect,
)
from post_prevention_mechanical_effect import (
    PostPreventionMechanicalEffect,
)


def test_post_prevention_mechanical_effect_stores_contract():
    effect = PostPreventionMechanicalEffect(
        effect_type=(
            MechanicalEffectType
            .POST_PREVENTION_EFFECT
        ),
        target=(
            MechanicalEffectTarget
            .POST_PREVENTION
        ),
        source_id="DRAIN_SOUL",
        post_prevention_effect=(
            PostPreventionEffect
            .REDUCE_WOUNDS_TO_ZERO
        ),
    )

    assert effect.effect_type is (
        MechanicalEffectType
        .POST_PREVENTION_EFFECT
    )
    assert effect.target is (
        MechanicalEffectTarget
        .POST_PREVENTION
    )
    assert (
        effect.post_prevention_effect
        is PostPreventionEffect
        .REDUCE_WOUNDS_TO_ZERO
    )


def test_post_prevention_mechanical_effect_rejects_wrong_type():
    with pytest.raises(
        ValueError,
        match="must use",
    ):
        PostPreventionMechanicalEffect(
            effect_type=(
                MechanicalEffectType.REROLL
            ),
            target=(
                MechanicalEffectTarget
                .POST_PREVENTION
            ),
            source_id="DRAIN_SOUL",
            post_prevention_effect=(
                PostPreventionEffect
                .REDUCE_WOUNDS_TO_ZERO
            ),
        )


def test_post_prevention_mechanical_effect_rejects_wrong_target():
    with pytest.raises(
        ValueError,
        match="target must be POST_PREVENTION",
    ):
        PostPreventionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .POST_PREVENTION_EFFECT
            ),
            target=(
                MechanicalEffectTarget.DUEL_ROLL
            ),
            source_id="DRAIN_SOUL",
            post_prevention_effect=(
                PostPreventionEffect
                .REDUCE_WOUNDS_TO_ZERO
            ),
        )


def test_post_prevention_mechanical_effect_rejects_invalid_effect():
    with pytest.raises(
        TypeError,
        match="post_prevention_effect",
    ):
        PostPreventionMechanicalEffect(
            effect_type=(
                MechanicalEffectType
                .POST_PREVENTION_EFFECT
            ),
            target=(
                MechanicalEffectTarget
                .POST_PREVENTION
            ),
            source_id="DRAIN_SOUL",
            post_prevention_effect=(
                "REDUCE_WOUNDS_TO_ZERO"
            ),
        )