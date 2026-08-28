import pytest

from resurrection_resilience_modifier import (
    calculate_resurrection_resilience_modifier,
)


def test_resurrection_bonus_is_scaled_by_resilience_weight():
    result = calculate_resurrection_resilience_modifier(
        expected_resurrection_bonus=1 / 3,
        resilience_weight=0.5,
    )

    assert result == pytest.approx(
        1 / 6,
    )


def test_zero_resurrection_bonus_produces_zero_modifier():
    result = calculate_resurrection_resilience_modifier(
        expected_resurrection_bonus=0.0,
        resilience_weight=0.5,
    )

    assert result == 0.0


def test_zero_resilience_weight_produces_zero_modifier():
    result = calculate_resurrection_resilience_modifier(
        expected_resurrection_bonus=0.5,
        resilience_weight=0.0,
    )

    assert result == 0.0


def test_full_bonus_and_full_weight_produce_full_modifier():
    result = calculate_resurrection_resilience_modifier(
        expected_resurrection_bonus=1.0,
        resilience_weight=1.0,
    )

    assert result == 1.0


def test_expected_resurrection_bonus_must_be_between_zero_and_one():
    with pytest.raises(ValueError):
        calculate_resurrection_resilience_modifier(
            expected_resurrection_bonus=1.1,
            resilience_weight=0.5,
        )


def test_resilience_weight_must_be_between_zero_and_one():
    with pytest.raises(ValueError):
        calculate_resurrection_resilience_modifier(
            expected_resurrection_bonus=0.5,
            resilience_weight=1.1,
        )


def test_boolean_inputs_are_rejected():
    with pytest.raises(TypeError):
        calculate_resurrection_resilience_modifier(
            expected_resurrection_bonus=True,
            resilience_weight=0.5,
        )