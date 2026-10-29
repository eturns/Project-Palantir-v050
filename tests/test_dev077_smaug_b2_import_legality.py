"""DEV-077-SMAUG-B2/E: import structure and negative legality tests."""
import copy
import json
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from importers.mesbg_list_builder_json_importer import build_army_definition_from_data

@pytest.fixture
def smaug_data():
    return json.loads((ROOT / 'tests/fixtures/smaug.json').read_text(encoding='utf-8'))

def test_valid_smaug_json_imports_as_single_compulsory_leader(smaug_data):
    army = build_army_definition_from_data(smaug_data)
    assert army.army_list_id == 'DESOLATOR_OF_THE_NORTH'
    assert army.leader_profile_id == 'SMAUG'
    assert army.leader_compulsory is True
    assert army.points_limit == 700
    assert len(army.entries) == 1
    assert army.entries[0].profile_id == 'SMAUG'
    assert army.entries[0].quantity == 1
    assert army.entries[0].is_warband_leader is True
    assert army.entries[0].is_compulsory is True

@pytest.mark.parametrize('mutate', [
    lambda d: d['warbands'].append(copy.deepcopy(d['warbands'][0])),
    lambda d: d['warbands'][0]['units'].append({'model_id':'[desolator-of-the-north] smaug','quantity':1,'options':[]}),
    lambda d: d['warbands'][0]['hero'].update(compulsory=False),
    lambda d: d['metadata'].update(leaderCompulsory=False),
    lambda d: d['metadata'].update(leader='other'),
    lambda d: d['metadata'].update(maxPoints=699),
    lambda d: d['warbands'][0]['hero']['options'].append({'id':'OPT_INVALID','quantity':1}),
])
def test_rejects_illegal_smaug_roster(smaug_data, mutate):
    mutate(smaug_data)
    with pytest.raises(ValueError):
        build_army_definition_from_data(smaug_data)
