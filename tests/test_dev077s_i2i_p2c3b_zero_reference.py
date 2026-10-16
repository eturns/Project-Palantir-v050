"""P2-C3-B: zero-to-frozen-maximum presentation calibration safeguards."""
from __future__ import annotations
import json
from pathlib import Path
import pytest

from provisional_calibration import (
    CalibrationError, CONDITIONAL, EVALUATED, NOT_EVALUATED,
    load_reference, rate_display,
)
from provisional_desktop_view import build_provisional_desktop_view, build_provisional_summary

REFERENCE = Path(__file__).resolve().parents[1] / 'data/calibration/provisional_six_army_v2.json'

@pytest.fixture(scope='module')
def reference():
    return load_reference(REFERENCE)

@pytest.mark.parametrize('metric', (
    'offence_density', 'stationary_shooting', 'open_ground_mobility',
    'courage_reliability', 'army_survival_density', 'per_model_resilience',
))
def test_real_zero_maps_to_zero_and_frozen_maximum_to_one(reference, metric):
    maximum = reference['metrics'][metric]['maximum']
    assert rate_display(metric, 0, reference).rating == 0.0
    assert rate_display(metric, maximum, reference).rating == 1.0
    assert rate_display(metric, maximum/2, reference).rating == pytest.approx(0.5)

@pytest.mark.parametrize('metric', (
    'offence_density', 'stationary_shooting', 'open_ground_mobility',
    'courage_reliability', 'army_survival_density', 'per_model_resilience',
))
def test_all_six_unchanged_frozen_reference_measurements(reference, metric):
    record = reference['metrics'][metric]
    for army in reference['armies']:
        raw = record['reference_raw_values'][army]
        result = rate_display(metric, raw, reference)
        assert result.rating == pytest.approx(raw / record['maximum'])
        assert result.raw_value == raw
        assert result.status == EVALUATED


def test_rangers_offence_no_longer_misleading_zero(reference):
    result = rate_display('offence_density', 0.6180555555555556, reference)
    assert result.rating == pytest.approx(0.4977783221531955, abs=0.00001)


def test_reference_is_immutable_with_new_armies(reference):
    before = rate_display('offence_density', 0.6180555555555556, reference)
    over = rate_display('offence_density', 500, reference)
    assert over.rating == 1 and over.clipped and over.raw_value == 500
    assert rate_display('offence_density', 0.6180555555555556, reference) == before


def test_missing_conditional_and_negative_distinguished(reference):
    assert rate_display('magic', None, reference).status == NOT_EVALUATED
    conditional = rate_display('offence_density', 0.618, reference, evidence_status=CONDITIONAL)
    assert conditional.rating is None and conditional.raw_value == 0.618
    with pytest.raises(CalibrationError):
        rate_display('offence_density', -0.1, reference)


def test_unknown_mapping_rejected(tmp_path, reference):
    altered = json.loads(json.dumps(reference))
    altered['metrics']['offence_density']['mapping_method'] = 'magic_numbers'
    path = tmp_path / 'invalid.json'
    path.write_text(json.dumps(altered))
    with pytest.raises(CalibrationError):
        load_reference(path)


def test_view_title_and_semantics(reference):
    panel = build_provisional_desktop_view(None, reference_path=REFERENCE)
    assert 'frozen six-army reference maximum' in panel['explanation']
    assert '0 = no measured output' in build_provisional_summary(panel)
    assert all(row['rating'] is None for row in panel['metrics'])
    assert panel['production_scoring_changed'] is False
    assert panel['defence_independent_composite_weighting_allowed'] is False
