from loader import (
    _load_profiles_from_file,
    load_all_profiles,
)
from rule_loader import (
    load_heroic_actions,
    load_special_rules,
)
from relationship_loader import (
    load_profile_heroic_actions,
    load_profile_special_rules,
)
from wargear_loader import load_wargear
from profile_default_wargear_loader import (
    load_profile_default_wargear,
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

def test_bard_profile_loads_correctly():
    profiles_by_id = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    bard = profiles_by_id["BARD"]

    assert bard.points == 130
    assert bard.movement == 6
    assert bard.fight == 5
    assert bard.shooting == "3+"
    assert bard.strength == 4
    assert bard.defence == 4
    assert bard.attacks == 3
    assert bard.wounds == 3
    assert bard.courage == "4+"
    assert bard.intelligence == "4+"
    assert bard.might == 3
    assert bard.will == 3
    assert bard.fate == 3
    assert bard.base_size_mm == 25

def test_bard_special_rules_load_correctly():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    bard = profiles_by_id["BARD"]

    rule_ids = {
        assignment.rule.id
        for assignment in bard.special_rules
    }

    assert {
        "SHARPSHOOTER",
        "RAPID_FIRE",
        "SWIFT_SHOT",
        "WINDLANCE_TRAINED",
        "BLACK_ARROW",
    }.issubset(rule_ids)

def test_bard_sworn_protector_targets_load_correctly():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    bard = profiles_by_id["BARD"]

    sworn_protector_targets = {
        assignment.parameter
        for assignment in bard.special_rules
        if assignment.rule.id == "SWORN_PROTECTOR"
    }

    assert sworn_protector_targets == {
        "BAIN",
        "SIGRID",
        "TILDA",
    }

def test_bards_family_static_profile_data_loads_correctly():
    profiles = {
        profile.id: profile
        for profile in load_all_profiles()
    }

    wargear = load_wargear()

    load_profile_default_wargear(
        profiles,
        wargear,
    )

    special_rules = load_special_rules()
    heroic_actions = load_heroic_actions()

    load_profile_special_rules(
        profiles,
        special_rules,
    )

    load_profile_heroic_actions(
        profiles,
        heroic_actions,
    )

    bain = profiles["BAIN"]
    sigrid = profiles["SIGRID"]
    tilda = profiles["TILDA"]

    assert {
        wargear.id
        for wargear in bain.default_wargear
    } == {
        "WG_HAND_WEAPON",
    }

    assert {
        action.id
        for action in bain.heroic_actions
    } == {
        "HEROIC_STRIKE",
    }

    assert {
        assignment.rule.id
        for assignment in bain.special_rules
    } == {
        "FAMILY_BOND",
    }

    assert {
        assignment.rule.id
        for assignment in sigrid.special_rules
    } == {
        "FEARFUL",
        "DA_DOWN_HERE",
    }

    assert {
        assignment.rule.id
        for assignment in tilda.special_rules
    } == {
        "FEARFUL",
        "DA_DOWN_HERE",
    }

    assert sigrid.default_wargear == []
    assert tilda.default_wargear == []