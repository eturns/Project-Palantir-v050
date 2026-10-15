"""B2 acceptance tests: reference construction and candidate normalisation."""
import pytest
from dataclasses import replace

from unified_calibration_contract import RawMeasurement, EvidenceAvailability, CalibrationApproval
from unified_calibration_benchmarks import (
    ReferenceAnchors, normalise_candidate, propose_reference_anchors,
    CANDIDATE_VERSION,
)


def ref(**changes):
    return replace(ReferenceAnchors('offence', 'fixture-A', 'wounds/turn', '700pt benchmark',
                                    'independent synthetic fixture', 2.0, 4.0, 8.0), **changes)


def obs(value=4.0, availability=EvidenceAvailability.AVAILABLE, **changes):
    unresolved = ('unknown line of sight',) if availability is EvidenceAvailability.PARTIAL else ()
    return replace(RawMeasurement('offence', value, 'wounds/turn', '700pt benchmark',
                                  'independent synthetic fixture', availability,
                                  unresolved=unresolved), **changes)


@pytest.mark.parametrize('value,expected', [(-3, 0), (2, 0), (3, .25),
                                              (4, .5), (6, .75), (8, 1), (20, 1)])
def test_piecewise_anchors(value, expected):
    result = normalise_candidate(obs(value), ref())
    assert result.candidate_score == pytest.approx(expected)
    assert result.production_score is None
    assert result.dashboard_rating is None
    assert result.scenario_score is None
    assert result.version == CANDIDATE_VERSION


@pytest.mark.parametrize('anchors', [dict(low=4), dict(typical=2), dict(high=4),
                                     dict(low=float('nan')), dict(high=float('inf'))])
def test_bad_anchors_rejected(anchors):
    with pytest.raises(ValueError):
        ref(**anchors)


def test_unapproved_reference_required():
    with pytest.raises(ValueError):
        ref(approval=CalibrationApproval.APPROVED)


def test_missing_reference_never_zero():
    r = normalise_candidate(obs(0), None)
    assert r.status == 'missing_reference' and r.candidate_score is None


def test_measured_zero_is_valid():
    r = normalise_candidate(obs(0), ref())
    assert r.candidate_score == 0 and r.status == 'candidate_only'


def test_unavailable_observation_never_scored():
    r = normalise_candidate(obs(None, EvidenceAvailability.UNAVAILABLE), ref())
    assert r.candidate_score is None and r.status == 'incomplete_evidence'


def test_partial_observation_never_fully_scored():
    r = normalise_candidate(obs(3, EvidenceAvailability.PARTIAL), ref())
    assert r.candidate_score is None and r.unresolved


def test_mismatched_unit_rejected():
    with pytest.raises(ValueError, match='Unit or population'):
        normalise_candidate(obs(unit='attacks'), ref())


def test_mismatched_population_rejected():
    with pytest.raises(ValueError, match='Unit or population'):
        normalise_candidate(obs(population='500pt benchmark'), ref())


def test_mismatched_metric_rejected():
    with pytest.raises(ValueError, match='Metric mismatch'):
        normalise_candidate(obs(), ref(metric='defence'))


def test_reference_from_observed_odd_sample():
    a = propose_reference_anchors(metric='offence', identifier='observed',
        unit='wounds/turn', population='700pt benchmark', provenance='fixture',
        observations=(8.0, 2.0, 4.0))
    assert (a.low, a.typical, a.high) == (2, 4, 8)


def test_reference_even_sample_median():
    a = propose_reference_anchors(metric='offence', identifier='observed',
        unit='wounds/turn', population='700pt benchmark', provenance='fixture',
        observations=(2.0, 3.0, 5.0, 8.0))
    assert (a.low, a.typical, a.high) == (2, 4, 8)


def test_degenerate_reference_sample_rejected():
    with pytest.raises(ValueError, match='strictly increasing'):
        propose_reference_anchors(metric='offence', identifier='observed',
            unit='wounds/turn', population='700pt benchmark', provenance='fixture',
            observations=(4.0, 4.0, 4.0))


@pytest.mark.parametrize('sample', [(1.0, 2.0), (1.0, float('nan'), 3.0),
                                     (True, 2.0, 3.0)])
def test_invalid_samples(sample):
    with pytest.raises(ValueError):
        propose_reference_anchors(metric='offence', identifier='observed',
            unit='wounds/turn', population='700pt benchmark', provenance='fixture',
            observations=sample)


def test_non_measurement_rejected():
    with pytest.raises(TypeError):
        normalise_candidate(4.0, ref())


def test_invalid_reference_type_rejected():
    with pytest.raises(TypeError):
        normalise_candidate(obs(), 'fake')
