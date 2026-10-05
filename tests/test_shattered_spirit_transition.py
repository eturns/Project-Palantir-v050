import pytest

from shattered_spirit_state import (
    ShatteredSpiritResult,
)
from shattered_spirit_transition import (
    resolve_shattered_spirit,
)


def test_successful_non_double_is_normal():
    state = resolve_shattered_spirit(
        first_die=2,
        second_die=4,
        intelligence="6+",
    )

    assert (
        state.result
        is ShatteredSpiritResult.NORMAL
    )


def test_successful_double_is_empowered():
    state = resolve_shattered_spirit(
        first_die=3,
        second_die=3,
        intelligence="6+",
    )

    assert (
        state.result
        is ShatteredSpiritResult.EMPOWERED
    )


def test_failed_test_is_opponent_controlled():
    state = resolve_shattered_spirit(
        first_die=2,
        second_die=3,
        intelligence="6+",
    )

    assert (
        state.result
        is ShatteredSpiritResult.OPPONENT_CONTROLLED
    )


def test_failed_double_is_still_opponent_controlled():
    state = resolve_shattered_spirit(
        first_die=2,
        second_die=2,
        intelligence="6+",
    )

    assert (
        state.result
        is ShatteredSpiritResult.OPPONENT_CONTROLLED
    )


def test_rejects_invalid_first_die():
    with pytest.raises(
        ValueError,
        match="first_die must be between 1 and 6",
    ):
        resolve_shattered_spirit(
            first_die=0,
            second_die=4,
            intelligence="6+",
        )


def test_rejects_invalid_second_die():
    with pytest.raises(
        ValueError,
        match="second_die must be between 1 and 6",
    ):
        resolve_shattered_spirit(
            first_die=3,
            second_die=7,
            intelligence="6+",
        )


def test_rejects_invalid_intelligence():
    with pytest.raises(
        ValueError,
        match=(
            "Intelligence value must be between "
            "3\\+ and 10\\+"
        ),
    ):
        resolve_shattered_spirit(
            first_die=3,
            second_die=3,
            intelligence="11+",
        )