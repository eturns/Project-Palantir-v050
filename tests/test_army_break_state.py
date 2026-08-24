import pytest

from army_break_state import (
    calculate_break_point,
    is_army_broken,
)
from army_model_state import ArmyModelState


@pytest.mark.parametrize(
    ("starting_models", "expected_break_point"),
    (
        (12, 6.0),
        (13, 6.5),
        (1, 0.5),
        (0, 0.0),
    ),
)
def test_calculate_break_point(
    starting_models,
    expected_break_point,
):
    assert calculate_break_point(
        starting_models,
    ) == expected_break_point


def test_even_army_is_not_broken_at_exactly_half_casualties():
    state = ArmyModelState(
        starting_models=12,
        remaining_models=6,
    )

    assert is_army_broken(state) is False


def test_even_army_is_broken_after_more_than_half_casualties():
    state = ArmyModelState(
        starting_models=12,
        remaining_models=5,
    )

    assert is_army_broken(state) is True


def test_odd_army_breaks_when_casualties_exceed_fractional_break_point():
    state = ArmyModelState(
        starting_models=13,
        remaining_models=6,
    )

    assert is_army_broken(state) is True


def test_odd_army_is_not_broken_before_break_point_is_exceeded():
    state = ArmyModelState(
        starting_models=13,
        remaining_models=7,
    )

    assert is_army_broken(state) is False


def test_empty_army_is_not_broken():
    state = ArmyModelState(
        starting_models=0,
        remaining_models=0,
    )

    assert is_army_broken(state) is False

def test_counted_models_can_prevent_army_from_being_broken():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=5,
    )

    assert is_army_broken(
        state,
        counted_models=1,
    ) is False


def test_counted_models_still_allow_army_to_be_broken_when_threshold_exceeded():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=4,
    )

    assert is_army_broken(
        state,
        counted_models=1,
    ) is True