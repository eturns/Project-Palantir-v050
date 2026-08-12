from manoeuvrability_inputs import ManoeuvrabilityInputs


def test_manoeuvrability_inputs_store_movement_and_base_size():
    inputs = ManoeuvrabilityInputs(
        movement=5,
        base_size_mm=25,
    )

    assert inputs.movement == 5
    assert inputs.base_size_mm == 25