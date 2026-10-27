"""DEV-077-TT-A: read-only contract for the supplied MESBG List Builder export.

Fixture location: tests/fixtures/the_three_trolls_all_options.json
No production code or canonical data is modified by this test.
"""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests' / 'fixtures' / 'the_three_trolls_all_options.json'

EXPECTED_MODELS = {
    '[the-three-trolls] bill-the-troll',
    '[the-three-trolls] bert-the-troll',
    '[the-three-trolls] tom-the-troll',
}
EXPECTED_UPGRADES = (
    'Full Bellies',
    'Stone Troll Endurance',
    'Nothing like a warm fire',
    'Rumbling Momentum',
    'Bowl them over',
    'Dominant presence',
    'Savvy Fighters',
    'Tasty Livestock',
    'Cover of Darkness',
    'Troll Cunning',
    'Kitchen Utensils',
    '"That\'s Mine That Is!"',
)


@pytest.fixture(scope='module')
def export():
    assert FIXTURE.is_file(), f'Copy the supplied JSON fixture to {FIXTURE}'
    return json.loads(FIXTURE.read_text(encoding='utf-8'))


def test_export_identifies_2024_three_trolls(export):
    assert export['edition'] == 'v2024'
    assert export['armyList'] == 'The Three Trolls'


def test_export_has_one_warband_and_all_three_models(export):
    assert len(export['warbands']) == 1
    warband = export['warbands'][0]
    models = {warband['hero']['model_id']} | {u['model_id'] for u in warband['units']}
    assert models == EXPECTED_MODELS
    assert all(u['quantity'] == 1 for u in warband['units'])


def test_bill_is_compulsory_leader(export):
    band = export['warbands'][0]
    assert export['metadata']['leaderCompulsory'] is True
    assert export['metadata']['leader'] == band['id']
    assert band['hero']['compulsory'] is True
    assert band['hero']['model_id'] == '[the-three-trolls] bill-the-troll'


def test_upgrades_are_army_level_not_profile_options(export):
    metadata = export['metadata']
    assert isinstance(metadata['tttSpecialUpgrades'], list)
    assert tuple(metadata['tttSpecialUpgrades']) == EXPECTED_UPGRADES
    band = export['warbands'][0]
    assert band['hero']['options'] == []
    assert all(u['options'] == [] for u in band['units'])


def test_no_duplicate_upgrade_selections(export):
    selections = export['metadata']['tttSpecialUpgrades']
    assert len(selections) == len(set(selections)) == 12


def test_export_warband_metadata_points_are_400(export):
    # This confirms the exported field, NOT the rules-correct final total.
    assert export['warbands'][0]['meta']['points'] == 400


def test_no_configured_points_limit_in_export(export):
    # Imported points_limit must remain None for this export.
    assert 'maxPoints' not in export['metadata']
