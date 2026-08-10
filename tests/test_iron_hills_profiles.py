import csv

from profiles import Profile
from iron_hills_test_helpers import (
    load_iron_hills_test_profiles,
)
def get_profile_by_id(
    profiles: list,
    profile_id: str,
):
    return next(
        profile
        for profile in profiles
        if profile.id == profile_id
    )


def test_iron_hills_warrior_profile_values():
    profiles = load_iron_hills_test_profiles()

    warrior = profiles[0]

    assert warrior.id == "IH_WR"
    assert warrior.name == "Iron Hills Warrior"
    assert warrior.points == 10
    assert warrior.movement == 5
    assert warrior.fight == 4
    assert warrior.shooting == "4+"
    assert warrior.strength == 4
    assert warrior.defence == 6
    assert warrior.attacks == 1
    assert warrior.wounds == 1
    assert warrior.courage == "6+"
    assert warrior.intelligence == "6+"
    assert warrior.might == 0
    assert warrior.will == 0
    assert warrior.fate == 0
    assert warrior.max_in_army == 0

def test_loads_dain_ironfoot():
    profiles = load_iron_hills_test_profiles()

    dain = get_profile_by_id(
        profiles,
        "IH_DAIN",
    )

    assert dain.name == (
        "Dáin Ironfoot Lord of the Iron Hills"
    )
    assert dain.points == 160
    assert dain.movement == 5
    assert dain.fight == 7
    assert dain.strength == 5
    assert dain.defence == 8
    assert dain.attacks == 3
    assert dain.wounds == 3
    assert dain.might == 3
    assert dain.will == 3
    assert dain.fate == 3
    assert dain.max_in_army == 1


def test_loads_iron_hills_captain():
    profiles = load_iron_hills_test_profiles()
    captain = get_profile_by_id(
            profiles,
            "IH_CAP",
        )
    
    assert captain.points == 80
    assert captain.movement == 5
    assert captain.fight == 5
    assert captain.defence == 8
    assert captain.attacks == 2
    assert captain.wounds == 2
    assert captain.might == 2
    assert captain.will == 1
    assert captain.fate == 1


def test_loads_iron_hills_goat_rider():
    profiles = load_iron_hills_test_profiles()
    rider = get_profile_by_id(
            profiles,
            "IH_GR",
        )
   
    assert rider.points == 20
    assert rider.movement == 5
    assert rider.fight == 4
    assert rider.strength == 4
    assert rider.defence == 6
    assert rider.attacks == 1
    assert rider.wounds == 1


def test_loads_iron_hills_chariot():
    profiles = load_iron_hills_test_profiles()
    chariot = get_profile_by_id(
            profiles,
            "IH_CHARIOT",
        )
    
    assert chariot.points == 170
    assert chariot.movement == 8
    assert chariot.fight == 4
    assert chariot.strength == 4
    assert chariot.defence == 8
    assert chariot.attacks == 2
    assert chariot.wounds == 4