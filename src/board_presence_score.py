from board_presence_inputs import BoardPresenceInputs


MODEL_PRESENCE_WEIGHT = 0.40
MANOEUVRABILITY_WEIGHT = 0.40
CONTROL_WEIGHT = 0.20


def calculate_board_presence(
    inputs: BoardPresenceInputs,
) -> float:
    return (
        inputs.model_presence * MODEL_PRESENCE_WEIGHT
        + inputs.manoeuvrability * MANOEUVRABILITY_WEIGHT
        + inputs.control * CONTROL_WEIGHT
    )