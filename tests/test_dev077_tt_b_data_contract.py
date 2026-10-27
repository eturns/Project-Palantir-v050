"""DEV-077-TT-B canonical roster/mapper acceptance tests."""
import csv
from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))


def rows(path):
    with (ROOT / path).open(encoding='utf-8-sig', newline='') as file:
        return list(csv.DictReader(file))


def test_three_trolls_army_registered():
    assert {'id':'THREE_TROLLS','name':'The Three Trolls','faction_id':'THREE_TROLLS'} in rows('data/factions/army_lists.csv')
    assert {'id':'THREE_TROLLS','name':'The Three Trolls'} in rows('data/factions/factions.csv')


def test_all_three_roster_members_registered():
    assert {r['profile_id'] for r in rows('data/factions/army_list_profiles.csv') if r['army_list_id']=='THREE_TROLLS'} == {'TT_BILL','TT_BERT','TT_TOM'}

@pytest.mark.parametrize('pid,points,fight,strength,defence,might,will,fate', [
    ('TT_BILL',150,8,7,7,3,1,1),
    ('TT_BERT',130,7,7,7,2,1,1),
    ('TT_TOM',120,7,6,6,1,3,1),
])
def test_canonical_profile(pid,points,fight,strength,defence,might,will,fate):
    row = next(r for r in rows('data/profiles/three_trolls_profiles.csv') if r['id']==pid)
    for field,want in [('points',points),('fight',fight),('strength',strength),('defence',defence),('might',might),('will',will),('fate',fate),('wounds',3),('attacks',3),('base_size_mm',60),('max_in_army',1)]:
        assert int(row[field]) == want
    assert row['races']=='TROLL'
    assert set(row['model_types'].split('|')) == {'INFANTRY', 'MONSTER'}
    assert row['max_in_army'] == '1'


def test_external_army_mapping():
    from importers.mesbg_list_builder_army_list_id_map import EXTERNAL_ARMY_LIST_IDS
    assert EXTERNAL_ARMY_LIST_IDS['The Three Trolls']=='THREE_TROLLS'


def test_external_profile_mappings():
    from importers.mesbg_list_builder_profile_id_map import EXTERNAL_PROFILE_IDS
    for name,pid in [('bill','TT_BILL'),('bert','TT_BERT'),('tom','TT_TOM')]:
        assert EXTERNAL_PROFILE_IDS[f'[the-three-trolls] {name}-the-troll']==pid


def test_profiles_load_without_duplicates(monkeypatch):
    monkeypatch.chdir(ROOT)
    from loader import load_all_profiles
    profiles = load_all_profiles()
    by_id = {p.id:p for p in profiles}
    assert len(by_id)==len(profiles)
    assert sum(by_id[p].points for p in ('TT_BILL','TT_BERT','TT_TOM'))==400


def test_all_options_remain_unimplemented_at_tt_b():
    """This stage registers the base army only, not the 50-point options."""
    assert not (ROOT/'data/rules/three_trolls_upgrades.csv').exists()
