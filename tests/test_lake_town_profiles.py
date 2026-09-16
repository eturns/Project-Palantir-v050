from loader import (
    _load_profiles_from_file,
    load_all_profiles,
)

def test_lake_town_family_profiles_load_correctly():
    profiles = _load_profiles_from_file(
        "data/profiles/lake_town_profiles.csv"
    )

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    bain = profiles_by_id["BAIN"]
    sigrid = profiles_by_id["SIGRID"]
    tilda = profiles_by_id["TILDA"]

    assert bain.points == 0
    assert bain.movement == 6
    assert bain.fight == 3
    assert bain.shooting == "4+"
    assert bain.strength == 3
    assert bain.defence == 3
    assert bain.attacks == 1
    assert bain.wounds == 2
    assert bain.courage == "6+"
    assert bain.intelligence == "7+"
    assert bain.might == 1
    assert bain.will == 3
    assert bain.fate == 2

    assert sigrid.points == 0
    assert sigrid.fight == 2
    assert sigrid.strength == 2
    assert sigrid.defence == 2
    assert sigrid.wounds == 1
    assert sigrid.courage == "7+"
    assert sigrid.might == 0
    assert sigrid.will == 1
    assert sigrid.fate == 2

    assert tilda.points == 0
    assert tilda.fight == 1
    assert tilda.strength == 2
    assert tilda.defence == 2
    assert tilda.wounds == 1
    assert tilda.courage == "8+"
    assert tilda.might == 0
    assert tilda.will == 1
    assert tilda.fate == 2

def test_lake_town_family_profiles_are_in_canonical_database():
    profiles_by_id = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    assert "BAIN" in profiles_by_id
    assert "SIGRID" in profiles_by_id
    assert "TILDA" in profiles_by_id