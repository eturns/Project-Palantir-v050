"""D5 quality-gate acceptance tests using the four uploaded real-army documents."""
import json
from pathlib import Path
from copy import deepcopy
import pytest
from i2i_c3_reference_population_gate import (
    ReferenceDescriptor, assess_population, load_evidence, main,
    METRICS, DEFAULT_REFERENCES,
)

HERE = Path(__file__).resolve().parent
SAMPLE_DIR = HERE.parent / 'docs' / 'validation' / 'i2i_c3'


def samples(tmp_path):
    paths = []
    for key, side, kind, filename in DEFAULT_REFERENCES:
        doc = json.loads((SAMPLE_DIR / filename).read_text(encoding='utf-8'))
        path = tmp_path / filename
        path.write_text(json.dumps(doc), encoding='utf-8')
        paths.append(ReferenceDescriptor(key, side, kind, str(path)))
    return tuple(paths)


def test_true_four_army_report(tmp_path):
    result = assess_population(samples(tmp_path))
    assert result['input_armies'] == 4
    assert result['target_point_armies'] == 1
    assert len(result['excluded_mixed_points']) == 3
    assert result['alignments'] == {'Evil': 1}
    assert len(result['metrics']) == 10
    assert all(not m['ready_for_anchor_review'] for m in result['metrics'])
    assert result['anchors_approved'] is False
    assert result['production_scoring_enabled'] is False


def test_only_dol_guldur_contributes_to_target_cohort(tmp_path):
    result = assess_population(samples(tmp_path))
    by_key = {m['metric']: m for m in result['metrics']}
    for metric in ('offence', 'defence', 'mobility', 'shooting', 'courage'):
        assert by_key[metric]['complete_target_point'] == 1
    assert by_key['magic']['partial_target_point'] == 1
    for metric in ('control', 'command', 'objective', 'hero_hunting'):
        assert by_key[metric]['unavailable_target_point'] == 1
    assert by_key['shooting']['nonzero_values'] == 0


def test_no_synthetic_assumptions_around_mixed_points(tmp_path):
    report = assess_population(samples(tmp_path))
    assert {e['points'] for e in report['excluded_mixed_points']} == {823, 177, 346}
    assert 'needs_3_good_target_point_armies' in report['population_blockers']


def test_duplicate_identity_fails(tmp_path):
    army = samples(tmp_path)[0]
    with pytest.raises(ValueError, match='Duplicate army'):
        assess_population((army, army))


def test_input_identity_fails(tmp_path):
    d = samples(tmp_path)[0]
    with pytest.raises(ValueError, match='Identity mismatch'):
        assess_population((ReferenceDescriptor('incorrect', d.alignment,
                                             d.archetype, d.evidence_path),))


def test_missing_file_does_not_become_zero(tmp_path):
    with pytest.raises(FileNotFoundError):
        assess_population((ReferenceDescriptor('x', 'Good', 'infantry',
                                             str(tmp_path / 'missing.json')),))


def test_invalid_numeric_data_rejected(tmp_path):
    d = samples(tmp_path)[0]
    doc = json.loads(Path(d.evidence_path).read_text())
    doc['measurements'][0]['value'] = float('nan')
    Path(d.evidence_path).write_text(json.dumps(doc))
    with pytest.raises(ValueError, match='finite'):
        assess_population((d,))


def test_invalid_zero_availability_rejected(tmp_path):
    d = samples(tmp_path)[0]
    doc = json.loads(Path(d.evidence_path).read_text())
    doc['measurements'][0]['availability'] = 'unavailable'
    Path(d.evidence_path).write_text(json.dumps(doc))
    with pytest.raises(ValueError, match='Unavailable metric'):
        assess_population((d,))


def test_attempt_to_enable_scoring_rejected(tmp_path):
    d = samples(tmp_path)[0]
    doc = json.loads(Path(d.evidence_path).read_text())
    doc['production_scoring_enabled'] = True
    Path(d.evidence_path).write_text(json.dumps(doc))
    with pytest.raises(ValueError, match='disabled'):
        assess_population((d,))


def test_partial_requires_reason(tmp_path):
    d = samples(tmp_path)[0]
    doc = json.loads(Path(d.evidence_path).read_text())
    doc['measurements'][3]['unresolved'] = []
    Path(d.evidence_path).write_text(json.dumps(doc))
    with pytest.raises(ValueError, match='unresolved'):
        assess_population((d,))


def test_cli_writes_research_only_and_refuses_overwrite(tmp_path, capsys):
    descriptors = samples(tmp_path)
    output = tmp_path / 'quality_report.json'
    result = main(['--evidence-dir', str(tmp_path), '--output', str(output)])
    assert result['anchors_approved'] is False
    assert json.loads(output.read_text())['purpose'] == 'reference_population_quality_diagnostic_only'
    with pytest.raises(SystemExit):
        main(['--evidence-dir', str(tmp_path), '--output', str(output)])


@pytest.mark.parametrize('metric', METRICS)
def test_canonical_metric_preserved(tmp_path, metric):
    report = assess_population(samples(tmp_path))
    assert metric in [x['metric'] for x in report['metrics']]


@pytest.mark.parametrize("points,accepted", [(694, False), (695, True), (697, True), (700, True), (701, False)])
def test_d7_cohort_points_boundary(tmp_path, points, accepted):
    d = samples(tmp_path)[0]
    doc = json.loads(Path(d.evidence_path).read_text())
    doc['points'] = points
    Path(d.evidence_path).write_text(json.dumps(doc))
    report = assess_population((d,))
    assert (report['target_point_armies'] == 1) is accepted
    assert report['research_policy']['min_reference_points'] == 695
    assert report['research_policy']['max_reference_points'] == 700
    assert not report['anchors_approved']


def test_d7_mixed_cohort_still_rejects_old_outliers(tmp_path):
    report = assess_population(samples(tmp_path))
    assert report['target_point_armies'] == 1
    assert sorted(x['points'] for x in report['excluded_mixed_points']) == [177, 346, 823]
