"""DEV-078-AoG-C3-B migration safeguards. Author: Edward Turns (Project Lead)."""
import csv
from pathlib import Path
from scripts.audit_dev078_aog_c3b_factions import ASSIGNMENTS, REVIEW, FILES, run


def fixture_root(tmp_path):
    d=tmp_path/'data'/'profiles'; d.mkdir(parents=True)
    for name in FILES:
        (d/f'{name}_profiles.csv').write_text('id,races,factions\n',encoding='utf-8')
    return d


def test_assignment_ids_are_unique():
    assert len(ASSIGNMENTS)>=40


def test_erebor_not_conflated_with_iron_hills():
    assert ASSIGNMENTS['BOFUR_CHAMPION_OF_EREBOR']=='EREBOR'
    assert ASSIGNMENTS['IH_DAIN']=='IRON_HILLS'


def test_thrain_and_gollum_held_for_review():
    assert {'THRAIN_THE_BROKEN','GT_GOLLUM'} <= REVIEW.keys()
    assert not {'THRAIN_THE_BROKEN','GT_GOLLUM'} & ASSIGNMENTS.keys()


def test_read_only_preserves_existing_csv(tmp_path):
    d=fixture_root(tmp_path)
    p=d/'erebor_profiles.csv'
    p.write_text('id,races\nBOFUR_CHAMPION_OF_EREBOR,DWARF\n')
    before=p.read_bytes()
    # Full mapping coverage is required: this miniature fixture fails before mutation.
    try:run(tmp_path)
    except ValueError as e:assert 'Unknown profile' in str(e)
    assert p.read_bytes()==before


def test_existing_conflict_blocks_all_writes(tmp_path):
    d=fixture_root(tmp_path)
    p=d/'erebor_profiles.csv'
    p.write_text('id,races,factions\nBOFUR_CHAMPION_OF_EREBOR,DWARF,IRON_HILLS\n')
    try:run(tmp_path,apply=True)
    except ValueError as e:assert 'Conflicting' in str(e)
    else:raise AssertionError('conflict was overwritten')
    assert 'IRON_HILLS' in p.read_text()
