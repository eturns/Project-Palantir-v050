import pytest

from dominant_presence import (
    get_dominant_presence_override,
    is_dominant_presence_active,
    resolve_dominant_presence_override,
)
from objective_control_override import (
    ObjectiveControlOverride,
    resolve_objective_control_override,
)

def test_dominant_presence_is_active_when_all_required_models_are_in_range():
    result = is_dominant_presence_active(
        required_models=3,
        models_in_range=3,
    )

    assert result is True


def test_dominant_presence_is_inactive_when_not_all_required_models_are_in_range():
    result = is_dominant_presence_active(
        required_models=3,
        models_in_range=2,
    )

    assert result is False


def test_extra_models_do_not_prevent_dominant_presence():
    result = is_dominant_presence_active(
        required_models=3,
        models_in_range=4,
    )

    assert result is True


def test_required_models_must_be_positive():
    with pytest.raises(ValueError):
        is_dominant_presence_active(
            required_models=0,
            models_in_range=0,
        )


def test_models_in_range_cannot_be_negative():
    with pytest.raises(ValueError):
        is_dominant_presence_active(
            required_models=3,
            models_in_range=-1,
        )


def test_model_counts_must_be_integers():
    with pytest.raises(TypeError):
        is_dominant_presence_active(
            required_models=3,
            models_in_range=2.5,
        )


def test_boolean_model_counts_are_rejected():
    with pytest.raises(TypeError):
        is_dominant_presence_active(
            required_models=True,
            models_in_range=3,
        )

def test_resolver_returns_automatic_control_when_all_required_models_are_present():
    result = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=3,
    )

    assert result == ObjectiveControlOverride.AUTOMATIC_CONTROL


def test_resolver_returns_no_override_when_required_models_are_missing():
    result = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=2,
    )

    assert result == ObjectiveControlOverride.NONE

def test_first_army_dominant_presence_wins_objective_override():
    first_override = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=3,
    )

    second_override = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=2,
    )

    result = resolve_objective_control_override(
        first_army_override=first_override,
        second_army_override=second_override,
    )

    assert result == 1


def test_second_army_dominant_presence_wins_objective_override():
    first_override = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=2,
    )

    second_override = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=3,
    )

    result = resolve_objective_control_override(
        first_army_override=first_override,
        second_army_override=second_override,
    )

    assert result == 2


def test_matching_dominant_presence_overrides_cancel():
    first_override = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=3,
    )

    second_override = resolve_dominant_presence_override(
        required_models=3,
        models_in_range=3,
    )

    result = resolve_objective_control_override(
        first_army_override=first_override,
        second_army_override=second_override,
    )

    assert result is None