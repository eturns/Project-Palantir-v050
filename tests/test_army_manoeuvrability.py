import pytest

from army import Army
from army_manoeuvrability import (
    calculate_army_manoeuvrability,
)
from profiles import Profile


def make_profile(
    *,
    profile_id: str,
    movement: float,
    base_size_mm: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
        movement=movement,
        fight=3,
        shooting="4+",
        strength=3,
        defence=3,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=0,
        base_size_mm=base_size_mm,
    )


def test_army_manoeuvrability_is_quantity_weighted_average():
    army = Army()

    army.add_profile(
        make_profile(
            profile_id="FAST",
            movement=10,
            base_size_mm=40,
        ),
        quantity=1,
    )

    army.add_profile(
        make_profile(
            profile_id="STANDARD",
            movement=6,
            base_size_mm=25,
        ),
        quantity=3,
    )

    result = calculate_army_manoeuvrability(
        army,
    )

    expected = (
        7.905694150420948
        + (6.0 * 3)
    ) / 4

    assert result == pytest.approx(expected)