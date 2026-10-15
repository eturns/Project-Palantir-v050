"""DEV-077S-I2-I-B3 reference sampling safeguards."""
from dataclasses import replace
import pytest
from unified_calibration_contract import RawMeasurement, EvidenceAvailability, CalibrationApproval
from unified_calibration_reference_sampling import (
    ReferenceArmy, SampleObservation, reference_army_plan, validate_reference_roster,
    sample_coverage, candidate_anchors_from_samples,
)


def armies():
    return (
        ReferenceArmy('elite', 'Dol Guldur', 'Evil', 'elite', 700, 'fixture/elite.json', 'sha1'),
        ReferenceArmy('line', 'Good infantry', 'Good', 'infantry', 700, 'fixture/line.json', 'sha2'),
        ReferenceArmy('rangers', 'Rangers', 'Good', 'shooting', 700, 'fixture/rangers.json', 'sha3'),
    )


def sample(army, val, status=EvidenceAvailability.AVAILABLE, *, unit='output/turn', context='target A', metric='offence'):
    unresolved = ('unverified',) if status is EvidenceAvailability.PARTIAL else ()
    if status is EvidenceAvailability.UNAVAILABLE:
        val = None
    return SampleObservation(army, 'fixture-v1', context,
        RawMeasurement(metric, val, unit, '700pt', 'synthetic test observation', status, unresolved=unresolved))


def samples():
    return (sample('elite', 1), sample('line', 2), sample('rangers', 3))


def test_plan_is_explicit_and_unmeasured():
    p = reference_army_plan()
    assert len(p) == 6 and any(row[0] == 'mirkwood_rangers' for row in p)
    assert all(row[-1] == 700 for row in p)

@pytest.mark.parametrize('points', [0, -1, 2.5, True])
def test_invalid_plan_points(points):
    with pytest.raises(ValueError): reference_army_plan(points)


def test_roster_validation():
    validate_reference_roster(armies())
    with pytest.raises(ValueError): validate_reference_roster(armies() + (armies()[0],))


def test_valid_candidate_coverage():
    c = sample_coverage('offence', armies(), samples())
    assert c.candidate_ready and c.distinct_armies == 3
    assert c.alignment_count == 2 and c.archetype_count == 3
    assert c.anchors_approved is False and c.production_scoring_enabled is False


def test_candidate_anchors_remain_proposed():
    a = candidate_anchors_from_samples('offence', 'example', armies(), samples())
    assert (a.low, a.typical, a.high) == (1, 2, 3)
    assert a.approval is CalibrationApproval.PROPOSED
    assert 'elite/fixture-v1' in a.provenance

@pytest.mark.parametrize('metric', ['unknown', 'Shooting', ''])
def test_unknown_metric(metric):
    with pytest.raises(ValueError): sample_coverage(metric, armies(), samples())


def test_unknown_army_rejected():
    with pytest.raises(ValueError): sample_coverage('offence', armies(), samples() + (sample('other', 4),))


def test_duplicate_sample_rejected():
    with pytest.raises(ValueError): sample_coverage('offence', armies(), samples() + (samples()[0],))


def test_partial_does_not_become_zero():
    ss = samples()[:2] + (sample('rangers', 0, EvidenceAvailability.PARTIAL),)
    c = sample_coverage('offence', armies(), ss)
    assert not c.candidate_ready and c.partial_count == 1
    with pytest.raises(ValueError): candidate_anchors_from_samples('offence', 'x', armies(), ss)


def test_unavailable_does_not_become_zero():
    ss = samples()[:2] + (sample('rangers', 0, EvidenceAvailability.UNAVAILABLE),)
    c = sample_coverage('offence', armies(), ss)
    assert c.unavailable_count == 1 and not c.candidate_ready


def test_unit_mismatch_rejected():
    ss = samples()[:2] + (sample('rangers', 3, unit='different'),)
    assert not sample_coverage('offence', armies(), ss).candidate_ready


def test_context_mismatch_rejected():
    ss = samples()[:2] + (sample('rangers', 3, context='target B'),)
    assert not sample_coverage('offence', armies(), ss).candidate_ready


def test_requires_two_alignments_by_default():
    aa = tuple(replace(a, alignment='Evil') for a in armies())
    assert not sample_coverage('offence', aa, samples()).candidate_ready
    assert sample_coverage('offence', aa, samples(), require_both_alignments=False).candidate_ready


def test_distinct_values_required():
    ss = (sample('elite', 1), sample('line', 1), sample('rangers', 2))
    assert not sample_coverage('offence', armies(), ss).candidate_ready


def test_minimum_armies_must_be_three():
    with pytest.raises(ValueError): sample_coverage('offence', armies(), samples(), min_armies=2)


def test_duplicate_army_observations_cannot_make_anchors():
    ss = samples() + (SampleObservation('elite', 'fixture-v2', 'target A',
                                      RawMeasurement('offence', 4, 'output/turn', '700pt', 'test', EvidenceAvailability.AVAILABLE)),)
    assert sample_coverage('offence', armies(), ss).candidate_ready
    with pytest.raises(ValueError): candidate_anchors_from_samples('offence', 'x', armies(), ss)


def test_wrong_sample_type():
    with pytest.raises(TypeError): sample_coverage('offence', armies(), ('invalid',))
