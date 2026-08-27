import pytest

from objective_control_override import (
    ObjectiveControlOverride,
    resolve_objective_control_override,
)


def test_no_overrides_returns_none():
    result = resolve_objective_control_override(
        first_army_override=ObjectiveControlOverride.NONE,
        second_army_override=ObjectiveControlOverride.NONE,
    )

    assert result is None


def test_first_army_override_wins_when_only_first_has_override():
    result = resolve_objective_control_override(
        first_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
        second_army_override=ObjectiveControlOverride.NONE,
    )

    assert result == 1


def test_second_army_override_wins_when_only_second_has_override():
    result = resolve_objective_control_override(
        first_army_override=ObjectiveControlOverride.NONE,
        second_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
    )

    assert result == 2


def test_matching_overrides_cancel():
    result = resolve_objective_control_override(
        first_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
        second_army_override=ObjectiveControlOverride.AUTOMATIC_CONTROL,
    )

    assert result is None


def test_invalid_first_override_rejected():
    with pytest.raises(
        TypeError,
        match="first_army_override must be an ObjectiveControlOverride.",
    ):
        resolve_objective_control_override(
            first_army_override="automatic_control",
            second_army_override=ObjectiveControlOverride.NONE,
        )


def test_invalid_second_override_rejected():
    with pytest.raises(
        TypeError,
        match="second_army_override must be an ObjectiveControlOverride.",
    ):
        resolve_objective_control_override(
            first_army_override=ObjectiveControlOverride.NONE,
            second_army_override="automatic_control",
        )