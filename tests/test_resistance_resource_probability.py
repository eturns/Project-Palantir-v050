import pytest

from resistance_resource_probability import (
    resist_will_refund_distribution,
)


def test_one_paid_resist_die_refund_distribution():
    distribution = (
        resist_will_refund_distribution(
            paid_dice_count=1,
        )
    )

    assert distribution[0] == pytest.approx(5 / 6)
    assert distribution[1] == pytest.approx(1 / 6)


def test_two_paid_resist_dice_refund_distribution():
    distribution = (
        resist_will_refund_distribution(
            paid_dice_count=2,
        )
    )

    assert distribution[0] == pytest.approx(25 / 36)
    assert distribution[1] == pytest.approx(10 / 36)
    assert distribution[2] == pytest.approx(1 / 36)


def test_refund_distribution_sums_to_one():
    distribution = (
        resist_will_refund_distribution(
            paid_dice_count=3,
        )
    )

    assert sum(distribution.values()) == pytest.approx(
        1.0
    )


def test_zero_paid_resist_dice_has_no_refund():
    assert resist_will_refund_distribution(
        paid_dice_count=0,
    ) == {
        0: 1.0,
    }


def test_refund_distribution_rejects_negative_dice():
    with pytest.raises(
        ValueError,
        match=(
            "Paid resistance dice count "
            "cannot be negative."
        ),
    ):
        resist_will_refund_distribution(
            paid_dice_count=-1,
        )