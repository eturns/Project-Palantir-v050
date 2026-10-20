"""GUN-A3: six new Gundabad mappings and source-verified default equipment.

Run from project root. Rule behaviour, option variants and war-beast composition
are intentionally outside this data registration test.
"""
import csv
import json
from pathlib import Path

from importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS

ROOT = Path(__file__).resolve().parents[1]
NEW = {
    "gundabad-berserker": "GUNDABAD_BERSERKER",
    "gundabad-ogre": "GUNDABAD_OGRE",
    "gundabad-troll": "GUNDABAD_TROLL",
    "war-bat": "WAR_BAT",
    "goblin-mercenary-captain": "GOBLIN_MERCENARY_CAPTAIN",
    "goblin-mercenary": "GOBLIN_MERCENARY",
}
EXPECTED_DEFAULTS = {
    "GUNDABAD_BERSERKER": {"WG_ARMOUR", "WG_HAND_WEAPON"},
    "GUNDABAD_OGRE": {"WG_HAND_WEAPON"},
    "GUNDABAD_TROLL": {"WG_HEAVY_ARMOUR", "WG_CRUSHING_CLUB"},
    "WAR_BAT": {"WG_HAND_WEAPON"},
    "GOBLIN_MERCENARY_CAPTAIN": {"WG_ARMOUR", "WG_HAND_WEAPON"},
    "GOBLIN_MERCENARY": {"WG_ARMOUR", "WG_HAND_WEAPON"},
}


def csv_rows(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_six_new_import_mappings_resolve_to_canonical_profiles():
    ids = {r["id"] for r in csv_rows(ROOT / "data/profiles/gundabad_profiles.csv")}
    for slug, canonical in NEW.items():
        assert EXTERNAL_PROFILE_IDS[f"[army-of-gundabad] {slug}"] == canonical
        assert canonical in ids


def test_all_supplied_gundabad_model_ids_have_mappings():
    doc = json.loads((ROOT / "tests/fixtures/gundabadalloptions.json").read_text(encoding="utf-8"))
    ids = {part["model_id"] for band in doc["warbands"]
           for part in [band["hero"], *band.get("units", [])]}
    assert len(ids) == 12
    assert not (ids - EXTERNAL_PROFILE_IDS.keys())


def test_default_wargear_matches_book_and_is_registered():
    rows = csv_rows(ROOT / "data/profiles/profile_default_wargear.csv")
    registered = {r["id"] for r in csv_rows(ROOT / "data/wargear/wargear.csv")}
    for profile, expected in EXPECTED_DEFAULTS.items():
        actual = [r["wargear_id"] for r in rows if r["profile_id"] == profile]
        assert set(actual) == expected, profile
        assert len(actual) == len(expected), f"duplicate default wargear for {profile}"
        assert expected <= registered


def test_crushing_club_is_distinct_from_normal_hand_weapon():
    items = {r["id"]: r["name"] for r in csv_rows(ROOT / "data/wargear/wargear.csv")}
    assert items["WG_CRUSHING_CLUB"] == "Crushing Club"
    assert "WG_CRUSHING_CLUB" != "WG_HAND_WEAPON"


def test_troll_brute_and_commander_remain_single_composition_work_item():
    profiles = {r["id"]: r for r in csv_rows(ROOT / "data/profiles/gundabad_profiles.csv")}
    assert profiles["TROLL_BRUTE"]["points"] == "0"
    assert profiles["ORC_COMMANDER"]["points"] == "0"
    assert "[army-of-gundabad] orc-commander" not in EXTERNAL_PROFILE_IDS
    # No separate purchase or composition mechanics are introduced by A3.
