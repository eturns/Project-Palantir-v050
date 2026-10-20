"""DEV-077-GUN-A2: 2024 Armies of the Hobbit Gundabad profile transcription.

Characteristics and classifications only. Mechanics, equipment and list legality
remain separate A3+ packages.
"""
import csv
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / 'data/profiles/gundabad_profiles.csv'

# id: points, movement, base, fight, shooting, strength, defence, attacks,
# wounds, courage, intelligence, might, will, fate, status, types, race
EXPECTED = {
    'GUNDABAD_BERSERKER': (15, '8"', 25, 4, '5+', 4, 5, 2, 1, '4+', '8+', 0, 0, 0, 'WARRIOR', 'INFANTRY', 'ORC'),
    'GUNDABAD_OGRE': (60, '8"', 50, 5, '6+', 6, 5, 3, 3, '7+', '7+', 0, 0, 0, 'WARRIOR', 'INFANTRY|MONSTER', 'OGRE'),
    'GUNDABAD_TROLL': (120, '6"', 80, 7, '4+', 7, 8, 3, 4, '6+', '7+', 0, 0, 0, 'WARRIOR', 'INFANTRY|MONSTER', 'TROLL'),
    'WAR_BAT': (25, '12"', 40, 3, '6+', 4, 4, 2, 2, '7+', '8+', 0, 0, 0, 'WARRIOR', 'INFANTRY|BEAST', 'BAT'),
    'GOBLIN_MERCENARY_CAPTAIN': (50, '5"', 25, 3, '5+', 4, 5, 2, 2, '7+', '6+', 2, 1, 1, 'HERO', 'INFANTRY', 'GOBLIN'),
    'GOBLIN_MERCENARY': (6, '5"', 25, 2, '5+', 3, 4, 1, 1, '8+', '7+', 0, 0, 0, 'WARRIOR', 'INFANTRY', 'GOBLIN'),
}


def profiles():
    with PATH.open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == len({row['id'] for row in rows}), 'Duplicate canonical profile IDs'
    return {row['id']: row for row in rows}


@pytest.mark.parametrize('profile_id', sorted(EXPECTED))
def test_new_profile_matches_official_2024_characteristics(profile_id):
    row = profiles()[profile_id]
    actual = (
        int(row['points']), row['movement'], int(row['base_size_mm']),
        int(row['fight']), row['shooting'], int(row['strength']),
        int(row['defence']), int(row['attacks']), int(row['wounds']),
        row['courage'], row['intelligence'], int(row['might']),
        int(row['will']), int(row['fate']), row['heroic_status'],
        row['model_types'], row['races'],
    )
    assert actual == EXPECTED[profile_id]
    assert row['max_in_army'] == '0'


def test_existing_gundabad_records_are_retained():
    known = {
        'GUNDABAD_CATAPULT_TROLL', 'ORC_COMMANDER', 'TROLL_BRUTE',
        'AZOG_THE_DEFILER', 'GUNDABAD_ORC_CAPTAIN', 'GUNDABAD_ORC_WARRIOR',
        'THRAIN_THE_BROKEN', 'WHITE_WARG_SEPARATED',
    }
    assert known.issubset(profiles())
    assert len(profiles()) == 14


def test_canonical_hero_and_warrior_types():
    rows = profiles()
    assert rows['GOBLIN_MERCENARY_CAPTAIN']['heroic_status'] == 'HERO'
    assert all(
        rows[profile]['heroic_status'] == 'WARRIOR'
        for profile in EXPECTED if profile != 'GOBLIN_MERCENARY_CAPTAIN'
    )
