import pytest
from manoeuvrability_inputs import ManoeuvrabilityInputs
from manoeuvrability_score import calculate_manoeuvrability


def test_25mm_model_preserves_raw_movement():
    inputs = ManoeuvrabilityInputs(
        movement=6,
        base_size_mm=25,
    )

    assert calculate_manoeuvrability(inputs) == 6.0


def test_40mm_fast_model_is_penalised_for_footprint():
    inputs = ManoeuvrabilityInputs(
        movement=10,
        base_size_mm=40,
    )

    assert calculate_manoeuvrability(inputs) == pytest.approx(
        7.9057,
        rel=1e-4,
    )


def test_60mm_fast_model_loses_more_usable_movement():
    inputs = ManoeuvrabilityInputs(
        movement=10,
        base_size_mm=60,
    )

    assert calculate_manoeuvrability(inputs) == pytest.approx(
        6.4550,
        rel=1e-4,
    )