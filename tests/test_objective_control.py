import pytest

from objective_control import (
    resolve_objective_control,
)
from objective_control_override import (
    ObjectiveControlOverride,
)


def test_first_army_controls_with_higher_presence():
    result = resolve_objective_control(
        first_army_presence=5,
        second_army_presence=3,
        first_army_override=ObjectiveControlOverride.NONE,
        second_army_override=ObjectiveControlOverride.NONE,
    )

    assert result == 1


def test_second_army_controls_with_higher_presence():
    result = resolve_objective_control(
        first_army_presence=2,
        second_army_presence=4,
        first_army_override=ObjectiveControlOverride.NONE,
        second_army_override=ObjectiveControlOverride.NONE,
    )

    assert result == 2


def test_equal_presence_returns_none():
    result = resolve_objective_control(
        first_army_presence=3,
        second_army_presence=3,
        first_army_override=ObjectiveControlOverride.NONE,
        second_army_override=ObjectiveControlOverride.NONE,
    )

    assert result is None


def test_first_army_override_takes_precedence_over_presence():
    result = resolve_objective_control(
        first_army_presence=1,
        second_army_presence=20,
        first_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
        second_army_override=ObjectiveControlOverride.NONE,
    )

    assert result == 1


def test_second_army_override_takes_precedence_over_presence():
    result = resolve_objective_control(
        first_army_presence=20,
        second_army_presence=1,
        first_army_override=ObjectiveControlOverride.NONE,
        second_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
    )

    assert result == 2


def test_matching_overrides_cancel_and_fall_back_to_presence():
    result = resolve_objective_control(
        first_army_presence=4,
        second_army_presence=2,
        first_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
        second_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
    )

    assert result == 1


def test_negative_first_presence_rejected():
    with pytest.raises(
        ValueError,
        match="first_army_presence cannot be negative.",
    ):
        resolve_objective_control(
            first_army_presence=-1,
            second_army_presence=0,
            first_army_override=ObjectiveControlOverride.NONE,
            second_army_override=ObjectiveControlOverride.NONE,
        )


def test_negative_second_presence_rejected():
    with pytest.raises(
        ValueError,
        match="second_army_presence cannot be negative.",
    ):
        resolve_objective_control(
            first_army_presence=0,
            second_army_presence=-1,
            first_army_override=ObjectiveControlOverride.NONE,
            second_army_override=ObjectiveControlOverride.NONE,
        )