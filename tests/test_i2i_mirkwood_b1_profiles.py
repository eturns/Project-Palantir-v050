"""B4-B1 regression: verified Mirkwood profile and faction registration only."""
import csv
from pathlib import Path

from loader import PROFILE_FILES, load_all_profiles, load_profile
from army_loader import load_army_lists, load_army_list_profiles, load_factions

EXPECTED = {
    "MW_LEGOLAS": (105, 6, "2+", 4, 5, 2, 2, "4+", "4+", 3, 2, 3),
    "MW_TAURIEL": (90, 6, "3+", 4, 5, 3, 2, "4+", "4+", 3, 2, 3),
    "MW_RANGER_CAPTAIN": (75, 6, "3+", 4, 4, 2, 2, "4+", "5+", 2, 1, 1),
    "MW_RANGER": (14, 5, "3+", 3, 3, 1, 1, "5+", "6+", 0, 0, 0),
}


def test_new_profile_file_registered_once():
    assert PROFILE_FILES.count("data/profiles/mirkwood_profiles.csv") == 1


def test_all_four_profiles_load():
    profiles = {p.id: p for p in load_all_profiles()}
    assert set(EXPECTED) <= set(profiles)


def test_four_profile_statistics():
    for pid, expected in EXPECTED.items():
        p = load_profile(pid)
        assert (p.points, p.fight, p.shooting, p.strength, p.defence,
                p.attacks, p.wounds, p.courage, p.intelligence,
                p.might, p.will, p.fate) == expected
        assert p.movement == 6
        assert p.base_size_mm == 25
        assert "ELF" in p.races


def test_warrior_and_heroes():
    profiles = {p.id: p for p in load_all_profiles()}
    assert profiles["MW_RANGER"].heroic_status.value == "WARRIOR"
    for pid in ("MW_LEGOLAS", "MW_TAURIEL", "MW_RANGER_CAPTAIN"):
        assert profiles[pid].heroic_status.value == "HERO"


def test_faction_and_army_list_load():
    factions = load_factions()
    assert "MIRKWOOD" in factions
    lists = load_army_lists(factions)
    assert "RANGERS_OF_MIRKWOOD" in lists
    assert lists["RANGERS_OF_MIRKWOOD"].faction.id == "MIRKWOOD"


def test_four_army_memberships():
    lists = load_army_lists(load_factions())
    profiles = {p.id: p for p in load_all_profiles()}
    load_army_list_profiles(lists, profiles)
    members = {p.id for p in lists["RANGERS_OF_MIRKWOOD"].profiles}
    assert members == set(EXPECTED)


def test_existing_armies_still_registered():
    assert {"DG_ROTN", "DG_PITS", "AZOGS_HUNTERS", "IH_IRON_HILLS"} <= set(
        load_army_lists(load_factions()))


def test_no_duplicate_profile_ids():
    ids = [p.id for p in load_all_profiles()]
    assert len(ids) == len(set(ids))
