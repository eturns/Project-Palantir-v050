"""I2-I-D3-A focused tests: diagnostics only, never calibrated ratings."""
import math
from pathlib import Path
import pytest
from i2i_d3a_candidate_scales import (
    ROOT, read_json, percentile_positions, transformations, build_report,
)

def test_tied_midrank():
    assert percentile_positions([1., 1., 3.]) == pytest.approx([.25,.25,1.])

def test_minmax_endpoints():
    assert transformations([2., 4., 6.])['minmax'] == [0.,.5,1.]

def test_median_ratio_not_clipped():
    assert transformations([1.,2.,10.])['median_ratio'] == [.5,1.,5.]

def test_constant_metric_not_forced_to_zero():
    assert transformations([5.,5.,5.])['minmax'] is None

def test_nonfinite_rejected():
    with pytest.raises(ValueError):
        transformations([math.nan,1.])

def test_unapproved_gate_blocks():
    assert build_report({}, {}, {})['status'] == 'blocked_by_evidence_gate'

@pytest.fixture(scope='module')
def report():
    paths = [ROOT/'i2i_d1_measurement_matrix.json',
             ROOT/'i2i_d2c_cross_metric_archetype_report.json',
             ROOT/'b8c_reference_qualification.json']
    if any(not p.exists() for p in paths):
        pytest.skip('Evidence JSON missing from project root')
    return build_report(*(read_json(p) for p in paths))

def test_scales_generated_for_six_metrics(report):
    assert report['status'] == 'illustrative_scales_complete',report
    assert len(report['scales'])==6

def test_two_defence_axes_mathematically_linked(report):
    assert 'dependency' in report['scales']['per_model_resilience']
    assert 'independent weighted metrics' in report['double_counting_rule']

def test_no_scores_or_approvals(report):
    assert report['calibration_anchors_approved'] is False
    assert report['numerical_calibration_permitted'] is False
    assert report['production_scoring_modified'] is False
    assert report['composite_score_calculated'] is False

def test_minmax_order_preserved(report):
    for metric in report['scales'].values():
        raw=metric['raw_values']
        transformed=metric['illustrative_transforms']['minmax']
        assert max(raw,key=raw.get)==max(transformed,key=transformed.get)
