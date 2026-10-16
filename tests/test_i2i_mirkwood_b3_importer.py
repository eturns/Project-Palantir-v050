"""DEV-077S-I2-I-C3-D7-B4-B3: importer mapping acceptance tests."""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from importers.mesbg_list_builder_army_list_id_map import EXTERNAL_ARMY_LIST_IDS
from importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS
from importers.mesbg_list_builder_json_importer import (
    build_configured_army_entry_definitions_from_data,
    get_palantir_army_list_id,
)

ROSTER = ROOT / "tests/fixtures/rangers-of-mirkwood.json"
PREFIX = "[rangers-of-mirkwood] "
EXPECTED = {
    PREFIX + "legolas-greenleaf-prince-of-mirkwood": "MW_LEGOLAS",
    PREFIX + "tauriel-ranger-of-mirkwood": "MW_TAURIEL",
    PREFIX + "mirkwood-ranger-captain": "MW_RANGER_CAPTAIN",
    PREFIX + "mirkwood-ranger": "MW_RANGER",
}


def roster():
    return json.loads(ROSTER.read_text(encoding="utf-8"))


def test_external_profile_mappings():
    assert {k: EXTERNAL_PROFILE_IDS.get(k) for k in EXPECTED} == EXPECTED


def test_external_army_list():
    assert EXTERNAL_ARMY_LIST_IDS["Rangers of Mirkwood"] == "RANGERS_OF_MIRKWOOD"
    assert get_palantir_army_list_id(roster()) == "RANGERS_OF_MIRKWOOD"


def test_actual_roster_entries_map_without_unknown_ids():
    entries = build_configured_army_entry_definitions_from_data(roster())
    counts = {}
    for entry in entries:
        counts[entry.profile_id] = counts.get(entry.profile_id, 0) + entry.quantity
    assert counts == {
        "MW_LEGOLAS": 1,
        "MW_TAURIEL": 1,
        "MW_RANGER_CAPTAIN": 1,
        "MW_RANGER": 30,
    }


def test_import_preserves_options_and_warbands():
    entries = build_configured_army_entry_definitions_from_data(roster())
    selected = {pid: set() for pid in ("MW_LEGOLAS", "MW_TAURIEL")}
    for entry in entries:
        if entry.profile_id in selected:
            selected[entry.profile_id].update(entry.external_option_ids)
    assert "OPT0771" in selected["MW_LEGOLAS"]
    assert "OPT0772" in selected["MW_TAURIEL"]
    assert len({e.warband_id for e in entries}) == 3


def test_canonical_ids_exist_in_profile_csv():
    with (ROOT / "data/profiles/mirkwood_profiles.csv").open(newline="", encoding="utf-8") as file:
        profiles = {row["id"] for row in csv.DictReader(file)}
    assert set(EXPECTED.values()) <= profiles


def test_existing_army_mappings_preserved():
    assert EXTERNAL_ARMY_LIST_IDS["Azog's Hunters"] == "AZOGS_HUNTERS"
    assert EXTERNAL_ARMY_LIST_IDS["The Iron Hills"] == "IH_IRON_HILLS"
    assert EXTERNAL_PROFILE_IDS["[azog's-hunters] azog-the-defiler"] == "AZOG_THE_DEFILER"


def test_all_mirkwood_profile_ids_distinct():
    assert len(set(EXPECTED.values())) == 4
