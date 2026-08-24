import pytest

from unholy_resurrection_marker_state import (
    UnholyResurrectionMarkerState,
)


def test_unholy_resurrection_marker_state_stores_marker_count():
    state = UnholyResurrectionMarkerState(
        marker_count=3,
    )

    assert state.marker_count == 3


def test_unholy_resurrection_marker_state_defaults_to_zero():
    state = UnholyResurrectionMarkerState()

    assert state.marker_count == 0


def test_unholy_resurrection_marker_state_rejects_negative_count():
    with pytest.raises(
        ValueError,
        match="Unholy Resurrection marker count cannot be negative.",
    ):
        UnholyResurrectionMarkerState(
            marker_count=-1,
        )


def test_unholy_resurrection_markers_count_for_army_strength():
    state = UnholyResurrectionMarkerState(
        marker_count=2,
    )

    assert state.counted_models == 2


def test_unholy_resurrection_markers_do_not_count_for_objectives():
    state = UnholyResurrectionMarkerState(
        marker_count=2,
    )

    assert state.objective_models == 0