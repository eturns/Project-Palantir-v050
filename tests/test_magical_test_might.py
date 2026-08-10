import pytest

from magical_test_might import (
    improve_magical_test_roll,
)


def test_might_improves_magical_test_roll():
    assert improve_magical_test_roll(
        roll=3,
        might_to_spend=1,
    ) == 4


def test_multiple_might_can_improve_roll():
    assert improve_magical_test_roll(
        roll=2,
        might_to_spend=2,
    ) == 4


def test_magical_test_roll_cannot_exceed_six():
    assert improve_magical_test_roll(
        roll=5,
        might_to_spend=3,
    ) == 6


def test_magical_test_might_rejects_negative_spend():
    with pytest.raises(
        ValueError,
        match="Might spend cannot be negative.",
    ):
        improve_magical_test_roll(
            roll=4,
            might_to_spend=-1,
        )