from math import sqrt

from manoeuvrability_inputs import ManoeuvrabilityInputs


def calculate_manoeuvrability(
    inputs: ManoeuvrabilityInputs,
) -> float:
    return inputs.movement / sqrt(
        inputs.base_size_mm / 25
    )