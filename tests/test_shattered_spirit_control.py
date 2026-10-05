from shattered_spirit_control import (
    can_owner_choose_activation,
    is_opponent_controlled,
)
from shattered_spirit_state import (
    ShatteredSpiritResult,
    ShatteredSpiritState,
)


def test_normal_shattered_spirit_remains_owner_controlled():
    state = ShatteredSpiritState()

    assert is_opponent_controlled(state) is False
    assert can_owner_choose_activation(state) is True


def test_empowered_shattered_spirit_remains_owner_controlled():
    state = ShatteredSpiritState(
        result=ShatteredSpiritResult.EMPOWERED,
    )

    assert is_opponent_controlled(state) is False
    assert can_owner_choose_activation(state) is True


def test_failed_shattered_spirit_is_opponent_controlled():
    state = ShatteredSpiritState(
        result=(
            ShatteredSpiritResult.OPPONENT_CONTROLLED
        ),
    )

    assert is_opponent_controlled(state) is True
    assert can_owner_choose_activation(state) is False