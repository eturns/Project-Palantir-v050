"""Read-only, conservative D1 regression and six-army data-contract tests."""
from pathlib import Path
import pytest
from i2i_d1_exploratory_measurement_matrix import (
    METRICS, benchmark_target, measure, build_report
)
from i2i_c3_b8c_reference_qualification import read_json

ROOT = Path(__file__).resolve().parents[1]


def test_five_metric_order():
    assert METRICS == ('offence', 'defence', 'mobility', 'shooting', 'courage')


def test_benchmark_is_fixed():
    target = benchmark_target()
    assert target.profile.fight == 4
    assert target.profile.defence == 6


def test_non_finite_measurement_rejected():
    with pytest.raises(ValueError):
        measure(float('nan'), 'units', 'assumptions')


def test_missing_gate_blocks():
    report = build_report({'stage': 'B8-C', 'status': 'blocked'})
    assert report['status'] == 'blocked_by_reference_gate'
    assert report['rows'] == []


def test_gate_never_enables_production_scoring():
    report = build_report({'stage': 'B8-C', 'status': 'blocked'})
    assert report['production_scoring_modified'] is False
    assert report['numerical_calibration_permitted'] is False


@pytest.fixture(scope='module')
def report():
    path = ROOT / 'b8c_reference_qualification.json'
    if not path.exists():
        pytest.skip('B8-C evidence file not present')
    return build_report(read_json(path))


def test_six_rows(report):
    assert len(report['rows']) == 6


def test_all_measurements_are_explicit(report):
    for row in report['rows']:
        assert set(row['measurements']) == set(METRICS)
        for metric in METRICS:
            item = row['measurements'][metric]
            assert item is None or item['approved'] is False


def test_no_numerical_approval(report):
    assert report['calibration_thresholds_fitted'] is False
    assert report['calibration_anchors_approved'] is False
    assert report['numerical_calibration_permitted'] is False
