import pytest

from defensive_resolution import (
    apply_post_prevention_effect,
    apply_unprevented_wounds,
    get_wounds_from_strike_damage,
)
from defensive_state import DefensiveState
from strike_damage import (
    StrikeDamage,
    StrikeDamageType,
)

from post_prevention_effect import PostPreventionEffect

def test_apply_unprevented_wounds_reduces_remaining_wounds():
    state = DefensiveState(
        remaining_wounds=3,
        remaining_fate=2,
    )

    result = apply_unprevented_wounds(
        state,
        wounds=1,
    )

    assert result == DefensiveState(
        remaining_wounds=2,
        remaining_fate=2,
    )


def test_apply_unprevented_wounds_can_reduce_model_to_zero_wounds():
    state = DefensiveState(
        remaining_wounds=2,
    )

    result = apply_unprevented_wounds(
        state,
        wounds=2,
    )

    assert result.remaining_wounds == 0


def test_apply_unprevented_wounds_does_not_reduce_below_zero():
    state = DefensiveState(
        remaining_wounds=1,
    )

    result = apply_unprevented_wounds(
        state,
        wounds=3,
    )

    assert result.remaining_wounds == 0


def test_apply_zero_wounds_leaves_state_unchanged():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=1,
    )

    result = apply_unprevented_wounds(
        state,
        wounds=0,
    )

    assert result == state


def test_apply_unprevented_wounds_rejects_negative_wounds():
    state = DefensiveState(
        remaining_wounds=2,
    )

    with pytest.raises(
        ValueError,
        match="Wounds to apply cannot be negative.",
    ):
        apply_unprevented_wounds(
            state,
            wounds=-1,
        )

def test_fixed_strike_damage_resolves_to_one_wound_by_default():
    damage = StrikeDamage()

    result = get_wounds_from_strike_damage(
        damage,
    )

    assert result == 1


def test_fixed_strike_damage_resolves_multiple_wounds():
    damage = StrikeDamage(
        wounds_per_successful_strike=2,
    )

    result = get_wounds_from_strike_damage(
        damage,
    )

    assert result == 2


def test_variable_strike_damage_is_not_resolved_deterministically():
    damage = StrikeDamage(
        damage_type=StrikeDamageType.D3,
    )

    with pytest.raises(
        ValueError,
        match="Only fixed StrikeDamage can be resolved deterministically.",
    ):
        get_wounds_from_strike_damage(
            damage,
        )

def test_no_post_prevention_effect_leaves_state_unchanged():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=1,
        remaining_will=3,
    )

    result = apply_post_prevention_effect(
        state,
        PostPreventionEffect.NONE,
    )

    assert result == state


def test_reduce_wounds_to_zero_slays_model():
    state = DefensiveState(
        remaining_wounds=3,
        remaining_fate=1,
        remaining_will=4,
    )

    result = apply_post_prevention_effect(
        state,
        PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO,
    )

    assert result.remaining_wounds == 0


def test_reduce_wounds_to_zero_preserves_other_resources():
    state = DefensiveState(
        remaining_wounds=3,
        remaining_fate=2,
        remaining_will=5,
    )

    result = apply_post_prevention_effect(
        state,
        PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO,
    )

    assert result.remaining_fate == 2
    assert result.remaining_will == 5