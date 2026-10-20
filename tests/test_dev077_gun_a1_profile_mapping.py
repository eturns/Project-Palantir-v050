"""GUN-A1 audit updated for A2/A3 canonical profile completion.

No army-list legality or points assumptions are made here.
"""
import csv
import json
from pathlib import Path

from importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests' / 'fixtures' / 'gundabadalloptions.json'
EXPECTED_MAPPED = {
    '[army-of-gundabad] azog-the-defiler': 'AZOG_THE_DEFILER',
    '[army-of-gundabad] bolg-spawn-of-azog': 'BOLG_SPAWN_OF_AZOG',
    '[army-of-gundabad] gundabad-orc-captain': 'GUNDABAD_ORC_CAPTAIN',
    '[army-of-gundabad] gundabad-orc-warrior': 'GUNDABAD_ORC_WARRIOR',
    '[army-of-gundabad] gundabad-catapult-troll': 'GUNDABAD_CATAPULT_TROLL',
    '[army-of-gundabad] troll-brute': 'TROLL_BRUTE',
}
EXPECTED_NEW = {
    '[army-of-gundabad] goblin-mercenary': 'GOBLIN_MERCENARY',
    '[army-of-gundabad] goblin-mercenary-captain': 'GOBLIN_MERCENARY_CAPTAIN',
    '[army-of-gundabad] gundabad-berserker': 'GUNDABAD_BERSERKER',
    '[army-of-gundabad] gundabad-ogre': 'GUNDABAD_OGRE',
    '[army-of-gundabad] gundabad-troll': 'GUNDABAD_TROLL',
    '[army-of-gundabad] war-bat': 'WAR_BAT',
}


def roster_ids():
    data = json.loads(FIXTURE.read_text(encoding='utf-8'))
    assert data['armyList'] == 'Army of Gundabad'
    return {record['model_id'] for warband in data['warbands']
            for record in (warband['hero'], *warband['units'])}


def registered_profile_ids():
    ids = set()
    for path in (ROOT / 'data' / 'profiles').glob('*_profiles.csv'):
        with path.open(encoding='utf-8-sig', newline='') as handle:
            ids.update(row['id'] for row in csv.DictReader(handle))
    return ids


def test_fixture_has_expected_unique_profiles():
    ids = roster_ids()
    assert len(ids) == 12
    assert ids == set(EXPECTED_MAPPED) | set(EXPECTED_NEW)


def test_all_six_reused_profiles_have_valid_canonical_ids():
    registered = registered_profile_ids()
    assert {k: EXTERNAL_PROFILE_IDS[k] for k in EXPECTED_MAPPED} == EXPECTED_MAPPED
    assert set(EXPECTED_MAPPED.values()) <= registered


def test_six_previously_unresolved_profiles_are_now_mapped_to_real_records():
    registered = registered_profile_ids()
    assert {key: EXTERNAL_PROFILE_IDS.get(key) for key in EXPECTED_NEW} == EXPECTED_NEW
    assert set(EXPECTED_NEW.values()) <= registered
    assert set(roster_ids()) <= EXTERNAL_PROFILE_IDS.keys()


def test_other_army_mappings_remain_available():
    assert EXTERNAL_PROFILE_IDS['[pits-of-dol-guldur] azog-the-defiler'] == 'AZOG_THE_DEFILER'
    assert EXTERNAL_PROFILE_IDS["[azog's-hunters] bolg-spawn-of-azog"] == 'BOLG_SPAWN_OF_AZOG'
    assert EXTERNAL_PROFILE_IDS['[the-iron-hills] iron-hills-warrior'] == 'IH_WR'


def test_same_catapult_troll_is_identified_in_both_roster_roles():
    data = json.loads(FIXTURE.read_text(encoding='utf-8'))
    external = '[army-of-gundabad] gundabad-catapult-troll'
    leaders = sum(band['hero']['model_id'] == external for band in data['warbands'])
    units = sum(item['model_id'] == external for band in data['warbands'] for item in band['units'])
    assert (leaders, units) == (1, 1)
    assert EXTERNAL_PROFILE_IDS[external] == 'GUNDABAD_CATAPULT_TROLL'
