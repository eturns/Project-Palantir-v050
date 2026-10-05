from shattered_spirit_state import (
    ShatteredSpiritResult,
    ShatteredSpiritState,
)


def test_shattered_spirit_defaults_to_normal():
    state = ShatteredSpiritState()

    assert (
        state.result
        is ShatteredSpiritResult.NORMAL
    )
    assert state.is_empowered is False
    assert state.is_opponent_controlled is False


def test_shattered_spirit_empowered_state():
    state = ShatteredSpiritState(
        result=ShatteredSpiritResult.EMPOWERED,
    )

    assert state.is_empowered is True
    assert state.is_opponent_controlled is False


def test_shattered_spirit_opponent_controlled_state():
    state = ShatteredSpiritState(
        result=(
            ShatteredSpiritResult.OPPONENT_CONTROLLED
        ),
    )

    assert state.is_empowered is False
    assert state.is_opponent_controlled is True