"""DEV-078-AoG-C3 — guarded affiliation migration acceptance tests.
Author: Edward Turns (Project Lead)
"""
import csv
from pathlib import Path
import pytest
from scripts.audit_dev078_aog_c3_profile_affiliations import FILES, REVIEWED, process

HEADERS = ('id', 'name', 'races', 'model_types')


def make_root(tmp_path):
    d = tmp_path / 'data' / 'profiles'
    d.mkdir(parents=True)
    for name in FILES:
        path = d / (name + '_profiles.csv')
        with path.open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
            if name == 'erebor':
                writer.writerow(('BOFUR_CHAMPION_OF_EREBOR', 'Bofur', 'DWARF', 'INFANTRY'))
            elif name == 'iron_hills':
                writer.writerow(('IH_WR', 'Iron Hills Warrior', 'DWARF', 'INFANTRY'))
            elif name == 'gundabad':
                writer.writerow(('THRAIN_THE_BROKEN', 'Thráin', 'DWARF', 'INFANTRY'))
    return tmp_path


def read_row(root, name):
    with (root / 'data' / 'profiles' / (name + '_profiles.csv')).open(newline='') as f:
        return next(csv.DictReader(f))


def test_readonly_does_not_modify_files(tmp_path):
    root = make_root(tmp_path)
    path = root / 'data/profiles/erebor_profiles.csv'
    original = path.read_bytes()
    process(root)
    assert path.read_bytes() == original


def test_apply_assigns_erebor_profile(tmp_path):
    root = make_root(tmp_path)
    process(root, apply=True)
    assert read_row(root, 'erebor')['factions'] == 'EREBOR'


def test_apply_assigns_iron_hills_not_erebor(tmp_path):
    root = make_root(tmp_path)
    process(root, apply=True)
    assert read_row(root, 'iron_hills')['factions'] == 'IRON_HILLS'


def test_apply_does_not_infer_thrain_as_gundabad(tmp_path):
    root = make_root(tmp_path)
    process(root, apply=True)
    assert read_row(root, 'gundabad')['factions'] == ''


def test_races_preserved(tmp_path):
    root = make_root(tmp_path)
    process(root, apply=True)
    assert read_row(root, 'erebor')['races'] == 'DWARF'


def test_twice_is_idempotent(tmp_path):
    root = make_root(tmp_path)
    process(root, apply=True)
    path = root / 'data/profiles/erebor_profiles.csv'
    first = path.read_bytes()
    process(root, apply=True)
    assert path.read_bytes() == first


def test_conflicting_reviewed_classification_rejected(tmp_path):
    root = make_root(tmp_path)
    path = root / 'data/profiles/erebor_profiles.csv'
    path.write_text('id,name,races,model_types,factions\nBOFUR_CHAMPION_OF_EREBOR,Bofur,DWARF,INFANTRY,IRON_HILLS\n')
    with pytest.raises(ValueError, match='conflicts'):
        process(root, apply=True)


def test_duplicate_profile_rejected(tmp_path):
    root = make_root(tmp_path)
    path = root / 'data/profiles/gundabad_profiles.csv'
    path.write_text('id,name,races,model_types\nBOFUR_CHAMPION_OF_EREBOR,Other,DWARF,INFANTRY\n')
    with pytest.raises(ValueError, match='Duplicate'):
        process(root)


def test_report_statuses(tmp_path):
    root = make_root(tmp_path)
    rows = process(root)
    assert any(r[1] == 'BOFUR_CHAMPION_OF_EREBOR' and r[4] == 'REVIEWED' for r in rows)
    assert any(r[1] == 'THRAIN_THE_BROKEN' and r[4] == 'NEEDS_CANONICAL_REVIEW' for r in rows)
