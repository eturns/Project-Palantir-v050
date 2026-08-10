from post_combat_wound_effect import (
    PostCombatWoundEffect,
)


def test_post_combat_wound_effect_defaults_to_none():
    effect = PostCombatWoundEffect()

    assert effect.additional_wound_on_roll is None


def test_post_combat_wound_effect_can_trigger_on_six():
    effect = PostCombatWoundEffect(
        additional_wound_on_roll=6,
    )

    assert effect.additional_wound_on_roll == 6