import pytest

from army import Army


def test_army_purchase_points_are_included_in_total():
    army = Army()

    army.add_purchase_points(60)

    assert army.total_points() == 60


def test_army_purchase_points_accumulate():
    army = Army()

    army.add_purchase_points(40)
    army.add_purchase_points(20)

    assert army.total_points() == 60


def test_army_purchase_points_cannot_be_negative():
    army = Army()

    with pytest.raises(
        ValueError,
        match="Purchase points must not be negative.",
    ):
        army.add_purchase_points(-1)