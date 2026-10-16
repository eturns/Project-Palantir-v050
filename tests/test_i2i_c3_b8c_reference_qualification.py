"""Focused B8-C decision tests using synthetic evidence; no production mutations."""
import copy
from pathlib import Path
from i2i_c3_b8a_cohort_intake import FIXTURES
from i2i_c3_b8c_reference_qualification import qualify, METRIC_POLICY, read_json


def fixtures():
    intake = {'stage': 'B8-A', 'intake_passed': 6, 'candidates': 6, 'results': []}
    for key, (filename, alignment, archetype) in FIXTURES.items():
        intake['results'].append({'key': key, 'file': f'tests/fixtures/{filename}',
                                  'alignment': alignment, 'proposed_archetype': archetype,
                                  'declared_points': 699, 'imported_points': 699,
                                  'models': 20, 'imported_models': 20,
                                  'status': 'intake_passed', 'issues': [],
                                  'archetype_review_approved': False})
    integration = {'stage': 'B8-B5', 'armies_imported': 6, 'import_errors': [],
                   'checks': [{'check': 'sample', 'status': 'verified'}],
                   'summary': {'blocked': 0}, 'calibration_anchors_approved': False}
    return intake, integration


def test_six_provisional_references_but_not_final_approval():
    intake, integration = fixtures()
    result = qualify(intake, integration)
    assert result['status'] == 'provisional_evidence_qualified'
    assert result['provisional_references'] == 6
    assert not result['numerical_calibration_permitted']
    assert not result['calibration_anchors_approved']


def test_balanced_three_good_three_evil():
    result = qualify(*fixtures())
    assert sum(x['alignment'] == 'Good' for x in result['armies']) == 3
    assert sum(x['alignment'] == 'Evil' for x in result['armies']) == 3
    assert len({x['proposed_archetype'] for x in result['armies']}) >= 4


def test_unavailable_metrics_not_zero_or_permitted():
    assert METRIC_POLICY['magic'] == 'partial_evidence_only'
    assert METRIC_POLICY['objective'] == 'requires_scenario_context'
    for x in qualify(*fixtures())['armies']:
        assert not x['full_mechanical_qualification_approved']
        assert not x['independent_archetype_approval']


def test_runtime_blocker_blocks_all():
    a, b = fixtures()
    b['checks'][0]['status'] = 'blocked'
    b['summary']['blocked'] = 1
    report = qualify(a, b)
    assert report['status'] == 'blocked' and report['provisional_references'] == 0


def test_import_point_mismatch_blocks_candidate():
    a, b = fixtures()
    a['results'][0]['imported_points'] = 690
    result = qualify(a, b)
    assert result['status'] == 'blocked'
    assert 'imported_points_mismatch' in result['armies'][0]['candidate_issues']


def test_wrong_fixture_name_blocks_candidate():
    a, b = fixtures()
    a['results'][0]['file'] = 'tests/fixtures/not_the_roster.json'
    assert qualify(a, b)['status'] == 'blocked'


def test_missing_check_records_block():
    a, b = fixtures()
    b['checks'] = []
    assert 'empty_runtime_evidence' in qualify(a, b)['qualification_errors']


def test_encoding_utf8_and_utf16(tmp_path):
    for encoding in ('utf-8-sig', 'utf-16'):
        path = tmp_path / f'{encoding}.json'
        path.write_text('{"ok": true}', encoding=encoding)
        assert read_json(path) == {'ok': True}


def test_chariot_remains_unapproved():
    result = qualify(*fixtures())
    iron = next(r for r in result['armies'] if r['army'] == 'iron_hills')
    assert 'chariot_platform_physical_behaviour_unverified' in iron['material_limitations']


def test_five_armies_bow_exchange_stays_qualified_not_fully_approved():
    result = qualify(*fixtures())
    row = next(r for r in result['armies'] if r['army'] == 'five_armies')
    assert row['candidate_status'] == 'provisional_reference'
    assert row['full_mechanical_qualification_approved'] is False
