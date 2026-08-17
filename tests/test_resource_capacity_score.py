import pytest

from resource_capacity_score import (
    calculate_resource_capacity_score,
)


def test_more_might_produces_higher_resource_capacity():
    eight_might_score = calculate_resource_capacity_score(
        might=8,
        will=30,
        fate=0,
        army_points=700,
    )

    ten_might_score = calculate_resource_capacity_score(
        might=10,
        will=30,
        fate=0,
        army_points=700,
    )

    assert ten_might_score > eight_might_score


def test_witch_king_might_increase_is_materially_visible():
    eight_might_score = calculate_resource_capacity_score(
        might=8,
        will=30,
        fate=0,
        army_points=700,
    )

    ten_might_score = calculate_resource_capacity_score(
        might=10,
        will=30,
        fate=0,
        army_points=700,
    )

    eight_might_capacity = (
        (8 / 700 * 100)
        / 1.5
    )

    ten_might_capacity = (
        (10 / 700 * 100)
        / 1.5
    )

    expected_eight_might_score = (
        eight_might_capacity
        + 1.0
        + 0.0
    ) / 3

    expected_ten_might_score = (
        ten_might_capacity
        + 1.0
        + 0.0
    ) / 3

    assert eight_might_score == pytest.approx(
        expected_eight_might_score,
    )

    assert ten_might_score == pytest.approx(
        expected_ten_might_score,
    )


def test_more_will_cannot_reduce_resource_capacity():
    lower_will_score = calculate_resource_capacity_score(
        might=6,
        will=8,
        fate=2,
        army_points=700,
    )

    higher_will_score = calculate_resource_capacity_score(
        might=6,
        will=10,
        fate=2,
        army_points=700,
    )

    assert higher_will_score > lower_will_score


def test_more_fate_cannot_reduce_resource_capacity():
    zero_fate_score = calculate_resource_capacity_score(
        might=8,
        will=30,
        fate=0,
        army_points=700,
    )

    one_fate_score = calculate_resource_capacity_score(
        might=8,
        will=30,
        fate=1,
        army_points=700,
    )

    assert one_fate_score > zero_fate_score


def test_resource_capacity_is_capped_at_one():
    score = calculate_resource_capacity_score(
        might=20,
        will=30,
        fate=10,
        army_points=700,
    )

    assert score == pytest.approx(
        1.0,
    )


def test_army_with_no_resources_has_zero_capacity():
    score = calculate_resource_capacity_score(
        might=0,
        will=0,
        fate=0,
        army_points=700,
    )

    assert score == 0.0