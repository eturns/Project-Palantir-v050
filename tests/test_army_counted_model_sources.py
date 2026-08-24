from army_break_state import is_army_broken
from army_counted_model_sources import (
    calculate_counted_models,
)
from army_model_state import ArmyModelState
from army_quarter_strength_state import (
    is_army_at_or_below_quarter_strength,
)
from unholy_resurrection_marker_state import (
    UnholyResurrectionMarkerState,
)


def test_calculate_counted_models_from_unholy_resurrection_markers():
    marker_state = UnholyResurrectionMarkerState(
        marker_count=2,
    )

    assert calculate_counted_models(
        marker_state,
    ) == 2


def test_unholy_resurrection_markers_can_prevent_broken_state():
    army_state = ArmyModelState(
        starting_models=11,
        remaining_models=5,
    )

    marker_state = UnholyResurrectionMarkerState(
        marker_count=1,
    )

    counted_models = calculate_counted_models(
        marker_state,
    )

    assert is_army_broken(
        army_state,
        counted_models=counted_models,
    ) is False


def test_unholy_resurrection_markers_can_prevent_quarter_strength():
    army_state = ArmyModelState(
        starting_models=11,
        remaining_models=2,
    )

    marker_state = UnholyResurrectionMarkerState(
        marker_count=1,
    )

    counted_models = calculate_counted_models(
        marker_state,
    )

    assert (
        is_army_at_or_below_quarter_strength(
            army_state,
            counted_models=counted_models,
        )
        is False
    )


def test_zero_unholy_resurrection_markers_do_not_change_army_state():
    army_state = ArmyModelState(
        starting_models=11,
        remaining_models=5,
    )

    marker_state = UnholyResurrectionMarkerState()

    counted_models = calculate_counted_models(
        marker_state,
    )

    assert counted_models == 0

    assert is_army_broken(
        army_state,
        counted_models=counted_models,
    ) is True