"""DEV-078-AoG-C3-B2: safeguarded 15-profile faction migration.
Author: Edward Turns (Project Lead)
"""
from pathlib import Path
import csv
import importlib.util
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'audit_dev078_aog_c3b2_final_factions.py'
spec = importlib.util.spec_from_file_location('dev078_aog_c3b2_faction_audit', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

@pytest.fixture
def fixture_root(tmp_path):
    path = tmp_path / 'data' / 'profiles'
    path.mkdir(parents=True)
    for name in module.FILES:
        profiles = [pid for pid in module.CONFIRMED if (
            (name == 'dol_guldur_profiles.csv' and pid in ('DG_HOC','DG_HOW','DG_HOWR','DG_FW','YAZNEG','NARZUG','FIMBUL')) or
            (name == 'gundabad_profiles.csv' and pid == 'THRAIN_THE_BROKEN') or
            (name == 'goblin_town_profiles.csv' and pid == 'GT_GOLLUM') or
            (name == 'three_trolls_profiles.csv' and pid in ('TT_BILL','TT_BERT','TT_TOM')) or
            (name == 'smaug_profiles.csv' and pid == 'SMAUG') or
            (name == 'beornings_profiles.csv' and pid in ('BEORN','BEORN_THE_BEAR'))
        )]
        with (path/name).open('w',encoding='utf-8',newline='') as f:
            w = csv.DictWriter(f, fieldnames=['id','races','factions','points'],lineterminator='\n')
            w.writeheader()
            w.writerows({'id':p,'races':'DWARF|SPIRIT','factions':'','points':'42'} for p in profiles)
    return tmp_path

def read(root,filename):
    with (root/'data'/'profiles'/filename).open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))

def test_all_fifteen_identifiers_are_distinct():
    assert len(module.CONFIRMED)==15

def test_spelling_is_preserved():
    assert module.CONFIRMED['GT_GOLLUM']=='GOBLIN-TOWN'
    assert module.CONFIRMED['TT_BILL']=='TROLLSHAWS'
    assert module.CONFIRMED['BEORN']=='BEORNING'

def test_dry_run_does_not_write(fixture_root):
    file = fixture_root/'data'/'profiles'/module.FILES[0]
    before=file.read_bytes()
    result=module.process(fixture_root)
    assert result['pending_assignments']==15 and file.read_bytes()==before

def test_apply_assigns_fifteen(fixture_root):
    result=module.process(fixture_root,apply=True)
    assert result['pending_assignments']==15
    all_rows=[r for n in module.FILES for r in read(fixture_root,n)]
    assert len(all_rows)==15
    assert all(r['factions']==module.CONFIRMED[r['id']] for r in all_rows)

def test_preserves_races_and_other_columns(fixture_root):
    module.process(fixture_root,apply=True)
    assert all(r['races']=='DWARF|SPIRIT' and r['points']=='42'
               for n in module.FILES for r in read(fixture_root,n))

def test_repeat_apply_is_noop(fixture_root):
    module.process(fixture_root,apply=True)
    before={n:(fixture_root/'data'/'profiles'/n).read_bytes() for n in module.FILES}
    result=module.process(fixture_root,apply=True)
    assert result['pending_assignments']==0 and result['files_to_update']==0
    assert before=={n:(fixture_root/'data'/'profiles'/n).read_bytes() for n in module.FILES}

def test_conflict_rejects_without_any_writes(fixture_root):
    path=fixture_root/'data'/'profiles'/'smaug_profiles.csv'
    path.write_text(path.read_text().replace('SMAUG,DWARF|SPIRIT,,42', 'SMAUG,DWARF|SPIRIT,GUNDABAD,42'))
    before={n:(fixture_root/'data'/'profiles'/n).read_bytes() for n in module.FILES}
    with pytest.raises(ValueError,match='Faction conflict'):
        module.process(fixture_root,apply=True)
    assert before=={n:(fixture_root/'data'/'profiles'/n).read_bytes() for n in module.FILES}

def test_missing_id_rejects_without_writes(fixture_root):
    path=fixture_root/'data'/'profiles'/'smaug_profiles.csv'
    path.write_text(path.read_text().replace('SMAUG,','NOT_SMAUG,'))
    before={n:(fixture_root/'data'/'profiles'/n).read_bytes() for n in module.FILES}
    with pytest.raises(ValueError,match='Unresolved confirmed IDs'):
        module.process(fixture_root,apply=True)
    assert before=={n:(fixture_root/'data'/'profiles'/n).read_bytes() for n in module.FILES}

def test_unrelated_row_unchanged(fixture_root):
    path=fixture_root/'data'/'profiles'/'smaug_profiles.csv'
    with path.open('a',encoding='utf-8') as f:
        f.write('OTHER,ORC,GUNDABAD,12\n')
    module.process(fixture_root,apply=True)
    assert read(fixture_root,'smaug_profiles.csv')[-1]=={'id':'OTHER','races':'ORC','factions':'GUNDABAD','points':'12'}

def test_normalisation_not_applied_to_hyphenated_value(fixture_root):
    module.process(fixture_root,apply=True)
    assert read(fixture_root,'goblin_town_profiles.csv')[0]['factions']=='GOBLIN-TOWN'
