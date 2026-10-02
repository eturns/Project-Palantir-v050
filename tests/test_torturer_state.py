import pytest

from torturer_state import TorturerState
from torturer_transition import (
    record_torturer_combat_kill,
)


def test_torturer_starts_with_no_bonuses():
    state = TorturerState()

    assert state.kills_in_combat == 0
    assert state.rerolls_natural_ones_to_wound is False
    assert state.gains_terror is False
    assert state.rerolls_all_failed_to_wound is False


def test_torturer_rerolls_ones_after_one_kill():
    state = TorturerState(
        kills_in_combat=1,
    )

    assert state.rerolls_natural_ones_to_wound is True
    assert state.gains_terror is False
    assert state.rerolls_all_failed_to_wound is False


def test_torturer_gains_terror_after_three_kills():
    state = TorturerState(
        kills_in_combat=3,
    )

    assert state.rerolls_natural_ones_to_wound is True
    assert state.gains_terror is True
    assert state.rerolls_all_failed_to_wound is False


def test_torturer_rerolls_all_failed_wounds_after_five_kills():
    state = TorturerState(
        kills_in_combat=5,
    )

    assert state.rerolls_natural_ones_to_wound is True
    assert state.gains_terror is True
    assert state.rerolls_all_failed_to_wound is True


def test_recording_kill_returns_new_state():
    original = TorturerState()

    updated = record_torturer_combat_kill(
        original,
    )

    assert original.kills_in_combat == 0
    assert updated.kills_in_combat == 1


def test_recording_multiple_kills_accumulates():
    state = TorturerState(
        kills_in_combat=2,
    )

    updated = record_torturer_combat_kill(
        state,
        kills=3,
    )

    assert updated.kills_in_combat == 5


def test_torturer_rejects_negative_kill_count():
    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        TorturerState(
            kills_in_combat=-1,
        )