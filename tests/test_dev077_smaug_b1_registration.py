"""DEV-077-SMAUG-B1/E: profile/data registration only; not mechanics completion."""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def rows(path):
    with (ROOT/path).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

def test_smaug_canonical_profile_and_geometry_source():
    entries=[r for r in rows('data/profiles/smaug_profiles.csv') if r['id']=='SMAUG']
    assert len(entries)==1
    r=entries[0]
    assert (r['name'],r['points'],r['movement'],r['fight'],r['shooting'])==('Smaug','700','12"','9','2+')
    assert [r[x] for x in ('strength','defence','attacks','wounds','courage','intelligence','might','will','fate')]==['9','9','4','20','4+','4+','3','6','0']
    assert (r['base_shape'],r['base_length_mm'],r['base_width_mm'])==('OVAL','231','133')
    assert r['max_in_army']=='1'

def test_smaug_list_membership_and_loader_registration():
    assert any(r['id']=='SMAUG' for r in rows('data/factions/factions.csv'))
    assert any(r['id']=='DESOLATOR_OF_THE_NORTH' and r['faction_id']=='SMAUG' for r in rows('data/factions/army_lists.csv'))
    assert any(r['army_list_id']=='DESOLATOR_OF_THE_NORTH' and r['profile_id']=='SMAUG' for r in rows('data/factions/army_list_profiles.csv'))
    assert '"data/profiles/smaug_profiles.csv"' in (ROOT/'src/loader.py').read_text(encoding='utf-8')

def test_smaug_loads_without_duplicates():
    import sys
    sys.path.insert(0,str(ROOT/'src'))
    from loader import load_all_profiles
    profiles=[p for p in load_all_profiles() if p.id=='SMAUG']
    assert len(profiles)==1
    assert profiles[0].points==700 and profiles[0].wounds==20
