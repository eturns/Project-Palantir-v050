"""DEV-077-GT-B source/data contract; copy to tests/ after installing data."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(relative: str) -> list[dict[str, str]]:
    with (ROOT / relative).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def test_goblin_town_has_six_profiles_with_verified_points() -> None:
    profiles = {p['id']: p for p in rows('data/profiles/goblin_town_profiles.csv')}
    assert {key: int(value['points']) for key, value in profiles.items()} == {
        'GT_KING': 150, 'GT_GRINNAH': 50, 'GT_SCRIBE': 50,
        'GT_CAPTAIN': 40, 'GT_GOLLUM': 40, 'GT_WARRIOR': 5,
    }


def test_profile_book_statlines() -> None:
    profiles = {p['id']: p for p in rows('data/profiles/goblin_town_profiles.csv')}
    assert (profiles['GT_KING']['attacks'], profiles['GT_KING']['wounds']) == ('3', '3')
    assert profiles['GT_SCRIBE']['movement'] == '0"'
    assert profiles['GT_WARRIOR']['defence'] == '3'
    assert profiles['GT_GOLLUM']['races'] == 'HOBBIT'


def test_army_list_membership() -> None:
    army_rows = [r for r in rows('data/factions/army_list_profiles.csv') if r['army_list_id'] == 'GOBLIN_TOWN']
    assert {r['profile_id'] for r in army_rows} == {
        'GT_KING', 'GT_GRINNAH', 'GT_SCRIBE', 'GT_CAPTAIN', 'GT_GOLLUM', 'GT_WARRIOR'
    }


def test_two_handed_option_and_wargear() -> None:
    matches = [r for r in rows('data/profiles/profile_options.csv') if r['external_id'] == 'OPT0709']
    assert len(matches) == 1
    assert (matches[0]['profile_id'], matches[0]['points']) == ('GT_WARRIOR', '1')
    assert any(r['option_id'] == matches[0]['id'] and r['wargear_id'] == 'WG_TWO_HANDED_WEAPON'
               for r in rows('data/profiles/profile_option_wargear.csv'))


def test_external_identifier_mappings() -> None:
    from src.importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS
    from src.importers.mesbg_list_builder_army_list_id_map import EXTERNAL_ARMY_LIST_IDS
    assert EXTERNAL_ARMY_LIST_IDS['Goblin-town'] == 'GOBLIN_TOWN'
    expected = {
        'the-goblin-king': 'GT_KING', 'grinnah-goblin-jailer': 'GT_GRINNAH',
        'the-goblin-scribe': 'GT_SCRIBE', 'goblin-captain': 'GT_CAPTAIN',
        'gollum': 'GT_GOLLUM', 'goblin-warrior': 'GT_WARRIOR',
    }
    for external, internal in expected.items():
        assert EXTERNAL_PROFILE_IDS[f'[goblin-town] {external}'] == internal


def test_profile_loader_registers_goblin_town() -> None:
    from src.loader import PROFILE_FILES
    assert 'data/profiles/goblin_town_profiles.csv' in PROFILE_FILES
