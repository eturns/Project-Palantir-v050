import pytest

from wound_capacity import (
    calculate_wound_capacity,
)


@pytest.mark.parametrize(
    "wounds, expected",
    [
        (1, 0.25),
        (2, 0.50),
        (3, 0.75),
        (4, 1.00),
        (5, 1.00),
    ],
)
def test_wound_capacity_scales_with_wounds(
    wounds,
    expected,
):
    result = calculate_wound_capacity(
        wounds=wounds,
    )

    assert result == pytest.approx(expected)


def test_wound_capacity_rejects_zero_wounds():
    with pytest.raises(
        ValueError,
        match="wounds must be at least 1.",
    ):
        calculate_wound_capacity(
            wounds=0,
        )


def test_wound_capacity_rejects_negative_wounds():
    with pytest.raises(
        ValueError,
        match="wounds must be at least 1.",
    ):
        calculate_wound_capacity(
            wounds=-1,
        )


def test_wound_capacity_rejects_non_integer_wounds():
    with pytest.raises(
        TypeError,
        match="wounds must be an int.",
    ):
        calculate_wound_capacity(
            wounds=1.5,
        )


def test_wound_capacity_rejects_boolean_wounds():
    with pytest.raises(
        TypeError,
        match="wounds must be an int.",
    ):
        calculate_wound_capacity(
            wounds=True,
        )