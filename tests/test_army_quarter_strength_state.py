import pytest

from army_model_state import ArmyModelState
from army_quarter_strength_state import (
    calculate_quarter_strength,
    is_army_at_or_below_quarter_strength,
)


@pytest.mark.parametrize(
    ("starting_models", "expected_quarter_strength"),
    (
        (12, 3.0),
        (11, 2.75),
        (13, 3.25),
        (1, 0.25),
        (0, 0.0),
    ),
)
def test_calculate_quarter_strength(
    starting_models,
    expected_quarter_strength,
):
    assert calculate_quarter_strength(
        starting_models,
    ) == expected_quarter_strength


def test_army_is_at_quarter_strength():
    state = ArmyModelState(
        starting_models=12,
        remaining_models=3,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is True
    )


def test_army_is_below_quarter_strength():
    state = ArmyModelState(
        starting_models=12,
        remaining_models=2,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is True
    )


def test_army_above_quarter_strength_does_not_qualify():
    state = ArmyModelState(
        starting_models=12,
        remaining_models=4,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is False
    )


def test_fractional_quarter_strength_does_not_round_up():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=3,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is False
    )


def test_fractional_quarter_strength_allows_lower_whole_model_count():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=2,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is True
    )


def test_thirteen_model_army_with_four_remaining_is_above_quarter_strength():
    state = ArmyModelState(
        starting_models=13,
        remaining_models=4,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is False
    )


def test_thirteen_model_army_with_three_remaining_is_below_quarter_strength():
    state = ArmyModelState(
        starting_models=13,
        remaining_models=3,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is True
    )


def test_empty_army_does_not_count_as_at_quarter_strength():
    state = ArmyModelState(
        starting_models=0,
        remaining_models=0,
    )

    assert (
        is_army_at_or_below_quarter_strength(state)
        is False
    )

def test_counted_models_can_prevent_army_reaching_quarter_strength():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=2,
    )

    assert (
        is_army_at_or_below_quarter_strength(
            state,
            counted_models=1,
        )
        is False
    )


def test_counted_models_still_allow_quarter_strength_when_threshold_met():
    state = ArmyModelState(
        starting_models=11,
        remaining_models=1,
    )

    assert (
        is_army_at_or_below_quarter_strength(
            state,
            counted_models=1,
        )
        is True
    )
    