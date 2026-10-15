"""Non-scoring acceptance tests for DEV-077S-I2-I-B1."""
import pytest

from unified_calibration_contract import (
    EvidenceAvailability, CalibrationApproval, RawMeasurement,
    BenchmarkSpecification, CalibratedCapability,
    build_calibration_architecture, validate_calibration_architecture,
)
from metric_constants import METRIC_NAMES


def raw(**overrides):
    fields = dict(metric='offence', value=0.0, unit='wounds/turn/100 points',
                  population='reference defender', provenance='fixture',
                  availability=EvidenceAvailability.AVAILABLE)
    fields.update(overrides)
    return RawMeasurement(**fields)


def test_canonical_order():
    assert build_calibration_architecture().metrics == METRIC_NAMES


def test_architecture_validation():
    validate_calibration_architecture()


def test_no_scoring_activation():
    a = build_calibration_architecture()
    assert not any((a.reference_values_approved, a.rating_thresholds_approved,
                    a.production_scoring_enabled))


def test_four_explicit_stages():
    assert len(build_calibration_architecture().pipeline) == 4


def test_raw_zero_is_genuine_observation():
    assert raw().value == 0


def test_missing_raw_measurement_not_zero():
    assert raw(value=None, availability=EvidenceAvailability.UNAVAILABLE).value is None


def test_partial_requires_unresolved():
    with pytest.raises(ValueError, match='unresolved'):
        raw(availability=EvidenceAvailability.PARTIAL)


def test_partial_with_reason_accepted():
    assert raw(availability=EvidenceAvailability.PARTIAL,
               unresolved=('target not verified',)).unresolved


def test_missing_value_cannot_be_available():
    with pytest.raises(ValueError):
        raw(value=None)


def test_unavailable_cannot_claim_number():
    with pytest.raises(ValueError):
        raw(availability=EvidenceAvailability.UNAVAILABLE)

@pytest.mark.parametrize('value', [float('nan'), float('inf'), True])
def test_bad_raw_values_rejected(value):
    with pytest.raises(ValueError):
        raw(value=value)


def test_unknown_metric_rejected():
    with pytest.raises(ValueError):
        raw(metric='something_else')


def test_empty_provenance_rejected():
    with pytest.raises(ValueError):
        raw(provenance='')


def test_benchmark_is_proposal_only():
    b = BenchmarkSpecification('offence', 'b1', '700-point reference armies',
                               'wounds/turn', 'fixture')
    assert b.reference_value is None and b.approval is CalibrationApproval.PROPOSED


def test_b1_must_not_approve_benchmark():
    with pytest.raises(ValueError):
        BenchmarkSpecification('offence', 'b1', 'army', 'wounds', 'fixture',
                               approval=CalibrationApproval.APPROVED)


def test_unavailable_calibrated_score_remains_none():
    c = CalibratedCapability('magic', None, EvidenceAvailability.UNAVAILABLE,
                             None, None, 'unavailable')
    assert c.score is None


def test_score_requires_traceability():
    with pytest.raises(ValueError):
        CalibratedCapability('offence', .5, EvidenceAvailability.AVAILABLE,
                             None, None, '')


def test_partial_cannot_claim_full_score():
    with pytest.raises(ValueError):
        CalibratedCapability('control', .4, EvidenceAvailability.PARTIAL,
                             'b1', 'v1', 'fixture')

@pytest.mark.parametrize('value', [-0.1, 1.1, float('nan'), True])
def test_invalid_calibrated_scores_rejected(value):
    with pytest.raises(ValueError):
        CalibratedCapability('offence', value, EvidenceAvailability.AVAILABLE,
                             'benchmark', 'v1', 'fixture')


def test_valid_scored_record_is_only_a_container():
    c = CalibratedCapability('offence', .5, EvidenceAvailability.AVAILABLE,
                             'benchmark', 'v1', 'fixture')
    assert c.score == .5


def test_required_safeguards_present():
    a = build_calibration_architecture()
    assert {'unavailable_is_not_zero', 'shared_resource_accounting',
            'scenario_mapping_separate', 'retain_legacy_comparison'} <= set(a.safeguards)
