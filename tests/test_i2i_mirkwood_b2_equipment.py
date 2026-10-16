"""DEV-077S-I2-I-C3-D7-B4-B2: focused Mirkwood equipment checks."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(path):
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))

def test_wargear_catalogue():
    items = {r["id"]: r["name"] for r in rows("data/wargear/wargear.csv")}
    assert items["WG_ELF_BOW"] == "Elf bow"
    assert items["WG_ELVEN_HAND_WEAPON"] == "Elven hand weapon"
    assert items["WG_ELVEN_CLOAK"] == "Elven cloak"

def test_default_wargear_exact():
    actual = {}
    for r in rows("data/profiles/profile_default_wargear.csv"):
        actual.setdefault(r["profile_id"], []).append(r["wargear_id"])
    expected = {
        "MW_LEGOLAS": {"WG_ARMOUR", "WG_ELVEN_HAND_WEAPON", "WG_ELF_BOW"},
        "MW_TAURIEL": {"WG_ARMOUR", "WG_ELVEN_HAND_WEAPON", "WG_ELVEN_CLOAK"},
        "MW_RANGER_CAPTAIN": {"WG_ELVEN_HAND_WEAPON", "WG_ELF_BOW", "WG_ELVEN_CLOAK"},
        "MW_RANGER": {"WG_ELVEN_HAND_WEAPON", "WG_ELF_BOW", "WG_ELVEN_CLOAK"},
    }
    for pid, gear in expected.items():
        assert set(actual[pid]) == gear
        assert len(actual[pid]) == len(gear)

def test_options_and_external_ids():
    opts = {r["id"]: r for r in rows("data/profiles/profile_options.csv")}
    assert opts["MW_LEGOLAS_CLOAK"]["profile_id"] == "MW_LEGOLAS"
    assert opts["MW_LEGOLAS_CLOAK"]["external_id"] == "OPT0771"
    assert int(opts["MW_LEGOLAS_CLOAK"]["points"]) == 5
    assert opts["MW_TAURIEL_BOW"]["profile_id"] == "MW_TAURIEL"
    assert opts["MW_TAURIEL_BOW"]["external_id"] == "OPT0772"
    assert int(opts["MW_TAURIEL_BOW"]["points"]) == 5

def test_option_grants():
    grants = {(r["option_id"], r["wargear_id"], r["action"]) for r in rows("data/profiles/profile_option_wargear.csv")}
    assert ("MW_LEGOLAS_CLOAK", "WG_ELVEN_CLOAK", "grant") in grants
    assert ("MW_TAURIEL_BOW", "WG_ELF_BOW", "grant") in grants

def test_elf_bow_mechanical_profile():
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    from ranged_weapon_profile import RANGED_WEAPON_PROFILES
    elf_bow = RANGED_WEAPON_PROFILES["WG_ELF_BOW"]
    assert elf_bow.is_mechanically_complete
    assert (elf_bow.range_inches, elf_bow.strength, elf_bow.shots) == (24, 3, 1)

def test_no_duplicated_csv_identifiers():
    for path, field in [
        ("data/wargear/wargear.csv", "id"),
        ("data/profiles/profile_options.csv", "id"),
    ]:
        values = [r[field] for r in rows(path)]
        assert len(values) == len(set(values)), path
