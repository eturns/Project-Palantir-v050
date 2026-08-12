from army import Army
from army_resource_totals import (
    calculate_army_resource_totals,
)
from army_resource_state import ArmyResourceState
from profiles import Profile


def create_profile(
    profile_id: str,
    *,
    might: int,
    will: int,
    fate: int,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=0,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=5,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=might,
        will=will,
        fate=fate,
        max_in_army=99,
    )


def test_calculate_army_resource_totals_sums_resources_by_quantity():
    hero = create_profile(
        "HERO",
        might=3,
        will=2,
        fate=1,
    )

    warrior = create_profile(
        "WARRIOR",
        might=0,
        will=0,
        fate=0,
    )

    army = Army()

    army.add_profile(
        hero,
        quantity=2,
    )

    army.add_profile(
        warrior,
        quantity=5,
    )

    totals = calculate_army_resource_totals(
        army,
    )

    assert totals == ArmyResourceState(
        might=6,
        will=4,
        fate=2,
    )


def test_empty_army_has_zero_resource_totals():
    army = Army()

    totals = calculate_army_resource_totals(
        army,
    )

    assert totals == ArmyResourceState(
        might=0,
        will=0,
        fate=0,
    )