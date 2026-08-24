import pytest

from army_model_state import ArmyModelState
from army_model_state_transition import (
    apply_model_casualties,
)


def test_apply_model_casualties_reduces_remaining_models():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=11,
    )

    next_state = apply_model_casualties(
        state,
        casualties=3,
    )

    assert next_state.starting_models == 11
    assert next_state.remaining_models == 8


def test_apply_model_casualties_does_not_mutate_original_state():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=11,
    )

    apply_model_casualties(
        state,
        casualties=3,
    )

    assert state.remaining_models == 11


def test_apply_zero_casualties_preserves_model_count():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=7,
    )

    next_state = apply_model_casualties(
        state,
        casualties=0,
    )

    assert next_state.remaining_models == 7


def test_apply_model_casualties_rejects_negative_casualties():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=7,
    )

    with pytest.raises(
        ValueError,
        match="Casualty count cannot be negative.",
    ):
        apply_model_casualties(
            state,
            casualties=-1,
        )


def test_apply_model_casualties_rejects_more_than_remaining_models():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=4,
    )

    with pytest.raises(
        ValueError,
        match="Casualty count cannot exceed remaining model count.",
    ):
        apply_model_casualties(
            state,
            casualties=5,
        )


def test_apply_model_casualties_can_reduce_army_to_zero():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=4,
    )

    next_state = apply_model_casualties(
        state,
        casualties=4,
    )

    assert next_state.remaining_models == 0