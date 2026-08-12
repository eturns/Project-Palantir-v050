import pytest

from board_presence_inputs import BoardPresenceInputs
from board_presence_score import calculate_board_presence


def test_board_presence_uses_locked_weighting():
    inputs = BoardPresenceInputs(
        model_presence=8,
        manoeuvrability=6,
        control=4,
    )

    assert calculate_board_presence(inputs) == pytest.approx(
        6.4
    )