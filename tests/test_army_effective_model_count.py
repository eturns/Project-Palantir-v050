from army_effective_model_count import (
    calculate_effective_model_count,
)
from army_model_state import ArmyModelState


def test_effective_model_count_defaults_to_remaining_models():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=6,
    )

    assert calculate_effective_model_count(
        state,
    ) == 6


def test_counted_markers_increase_effective_model_count():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=5,
    )

    assert calculate_effective_model_count(
        state,
        counted_models=2,
    ) == 7


def test_removed_but_counted_models_increase_effective_model_count():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=4,
    )

    assert calculate_effective_model_count(
        state,
        counted_models=3,
    ) == 7


def test_effective_model_count_cannot_exceed_starting_models():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=10,
    )

    assert calculate_effective_model_count(
        state,
        counted_models=5,
    ) == 11


def test_zero_counted_models_does_not_change_state():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=5,
    )

    assert calculate_effective_model_count(
        state,
        counted_models=0,
    ) == 5