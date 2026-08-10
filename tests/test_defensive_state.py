import pytest

from defensive_state import DefensiveState


def test_defensive_state_stores_remaining_wounds():
    state = DefensiveState(
        remaining_wounds=2,
    )

    assert state.remaining_wounds == 2


def test_defensive_state_defaults_to_zero_fate():
    state = DefensiveState(
        remaining_wounds=2,
    )

    assert state.remaining_fate == 0


def test_defensive_state_stores_remaining_fate():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_fate=3,
    )

    assert state.remaining_fate == 3


def test_defensive_state_rejects_negative_wounds():
    with pytest.raises(
        ValueError,
        match="Remaining wounds cannot be negative.",
    ):
        DefensiveState(
            remaining_wounds=-1,
        )


def test_defensive_state_rejects_negative_fate():
    with pytest.raises(
        ValueError,
        match="Remaining Fate cannot be negative.",
    ):
        DefensiveState(
            remaining_wounds=1,
            remaining_fate=-1,
        )

def test_defensive_state_defaults_to_zero_will():
    state = DefensiveState(
        remaining_wounds=2,
    )

    assert state.remaining_will == 0


def test_defensive_state_stores_remaining_will():
    state = DefensiveState(
        remaining_wounds=2,
        remaining_will=25,
    )

    assert state.remaining_will == 25


def test_defensive_state_rejects_negative_will():
    with pytest.raises(
        ValueError,
        match="Remaining Will cannot be negative.",
    ):
        DefensiveState(
            remaining_wounds=1,
            remaining_will=-1,
        )