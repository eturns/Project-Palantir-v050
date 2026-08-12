from board_presence_inputs import BoardPresenceInputs


def test_board_presence_inputs_store_values():
    inputs = BoardPresenceInputs(
        model_presence=10,
        manoeuvrability=6.45,
        control=3,
    )

    assert inputs.model_presence == 10
    assert inputs.manoeuvrability == 6.45
    assert inputs.control == 3