from loader import load_all_profiles
from wargear_loader import load_wargear
from profile_default_wargear_loader import (
    load_profile_default_wargear,
)
from relationship_loader import (
    load_profile_heroic_actions,
)
from rule_loader import load_heroic_actions


def load_azogs_hunters_profiles():
    profiles_by_id = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    wargear = load_wargear()

    load_profile_default_wargear(
        profiles=profiles_by_id,
        wargear=wargear,
    )

    heroic_actions = load_heroic_actions()

    load_profile_heroic_actions(
        profiles=profiles_by_id,
        heroic_actions=heroic_actions,
    )

    return profiles_by_id


def test_bolg_profile_data():
    profiles = load_azogs_hunters_profiles()
    bolg = profiles["BOLG_SPAWN_OF_AZOG"]

    assert (
        bolg.name,
        bolg.points,
        bolg.movement,
        bolg.fight,
        bolg.shooting,
        bolg.strength,
        bolg.defence,
        bolg.attacks,
        bolg.wounds,
        bolg.courage,
        bolg.intelligence,
        bolg.might,
        bolg.will,
        bolg.fate,
        bolg.max_in_army,
    ) == (
        "Bolg, Spawn of Azog",
        175,
        6,
        7,
        "4+",
        5,
        7,
        3,
        3,
        "5+",
        "5+",
        3,
        3,
        1,
        1,
    )

    assert bolg.races == {"ORC"}

    assert {
        item.id
        for item in bolg.default_wargear
    } == {
        "WG_HEAVY_ARMOUR",
        "WG_TWO_HANDED_WEAPON",
    }

    assert {
        action.id
        for action in bolg.heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_CHALLENGE",
        "HEROIC_MARCH",
        "HEROIC_STRENGTH",
        "HEROIC_STRIKE",
    }


def test_yazneg_profile_data():
    profiles = load_azogs_hunters_profiles()
    yazneg = profiles["YAZNEG"]

    assert (
        yazneg.name,
        yazneg.points,
        yazneg.movement,
        yazneg.fight,
        yazneg.shooting,
        yazneg.strength,
        yazneg.defence,
        yazneg.attacks,
        yazneg.wounds,
        yazneg.courage,
        yazneg.intelligence,
        yazneg.might,
        yazneg.will,
        yazneg.fate,
        yazneg.max_in_army,
    ) == (
        "Yazneg, Hunter Orc Captain",
        55,
        6,
        5,
        "5+",
        4,
        5,
        2,
        2,
        "6+",
        "6+",
        3,
        1,
        1,
        1,
    )

    assert yazneg.races == {"ORC"}

    assert {
        item.id
        for item in yazneg.default_wargear
    } == {
        "WG_ARMOUR",
        "WG_TWO_HANDED_WEAPON",
    }

    assert {
        action.id
        for action in yazneg.heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_STRIKE",
    }


def test_narzug_profile_data():
    profiles = load_azogs_hunters_profiles()
    narzug = profiles["NARZUG"]

    assert (
        narzug.name,
        narzug.points,
        narzug.movement,
        narzug.fight,
        narzug.shooting,
        narzug.strength,
        narzug.defence,
        narzug.attacks,
        narzug.wounds,
        narzug.courage,
        narzug.intelligence,
        narzug.might,
        narzug.will,
        narzug.fate,
        narzug.max_in_army,
    ) == (
        "Narzug, Hunter Orc Captain",
        55,
        6,
        4,
        "3+",
        4,
        4,
        2,
        2,
        "6+",
        "6+",
        2,
        2,
        1,
        1,
    )

    assert narzug.races == {"ORC"}

    assert {
        item.id
        for item in narzug.default_wargear
    } == {
        "WG_LIGHT_ARMOUR",
        "WG_HAND_WEAPON",
        "WG_ORC_BOW",
    }

    assert {
        action.id
        for action in narzug.heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_ACCURACY",
    }


def test_fimbul_profile_data():
    profiles = load_azogs_hunters_profiles()
    fimbul = profiles["FIMBUL"]

    assert (
        fimbul.name,
        fimbul.points,
        fimbul.movement,
        fimbul.fight,
        fimbul.shooting,
        fimbul.strength,
        fimbul.defence,
        fimbul.attacks,
        fimbul.wounds,
        fimbul.courage,
        fimbul.intelligence,
        fimbul.might,
        fimbul.will,
        fimbul.fate,
        fimbul.max_in_army,
    ) == (
        "Fimbul, Hunter Orc Captain",
        50,
        6,
        4,
        "5+",
        4,
        5,
        2,
        2,
        "6+",
        "7+",
        2,
        1,
        1,
        1,
    )

    assert fimbul.races == {"ORC"}

    assert {
        item.id
        for item in fimbul.default_wargear
    } == {
        "WG_ARMOUR",
        "WG_HAND_WEAPON",
    }

    assert {
        action.id
        for action in fimbul.heroic_actions
    } == {
        "HEROIC_MOVE",
        "HEROIC_SHOOT",
        "HEROIC_COMBAT",
        "HEROIC_STRENGTH",
    }
