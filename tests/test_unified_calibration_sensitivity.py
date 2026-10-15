"""DEV-077S-I2-I-B4 tests: synthetic observations, no production scoring."""
import pytest
from unified_calibration_contract import RawMeasurement, EvidenceAvailability as E
from unified_calibration_benchmarks import ReferenceAnchors
from unified_calibration_sensitivity import (SensitivityObservation, compare_benchmark_sensitivity,
    describe_cohorts, local_score_sensitivity)


def anchors(identifier='base', low=0, typical=10, high=20, metric='offence', unit='damage'):
    return ReferenceAnchors(metric, identifier, unit, '700-point army', 'synthetic-test', low, typical, high)


def measure(value, availability=E.AVAILABLE, metric='offence', unit='damage'):
    return RawMeasurement(metric, value, unit, '700-point army', 'synthetic-test', availability,
                          unresolved=('missing assumption',) if availability is E.PARTIAL else ())


def obs(key, value, alignment='Evil', archetype='elite', availability=E.AVAILABLE):
    return SensitivityObservation(key, alignment, archetype, measure(value, availability))


def report():
    return compare_benchmark_sensitivity((obs('a', 5), obs('b', 10, 'Good', 'shooting'),
                                         obs('c', 15, 'Evil', 'infantry')),
                                         anchors(), (anchors('alternative', 0, 5, 25),))


def test_three_paired_scores():
    assert report().paired_count == 3


def test_alternative_anchor_identity():
    assert report().alternative_ids == ('alternative',)


def test_candidate_scores_exact():
    assert report().rows[1].base_score == pytest.approx(.5)


def test_shift_detected():
    assert report().greatest_shift > 0


def test_mean_shift_reported():
    assert report().mean_shift > 0


def test_ranking_reversals_not_invented():
    assert report().ranking_reversals == 0


def test_paired_comparisons_count():
    assert report().evaluated_pairs == 3


def test_production_never_enabled():
    r=report()
    assert not r.production_scoring_enabled and not r.benchmarks_approved and not r.fairness_certified


def test_partial_not_zero():
    r=compare_benchmark_sensitivity((obs('a', 7, availability=E.PARTIAL),), anchors(), (anchors('other', 1, 11, 21),))
    assert r.rows[0].base_score is None and r.incomplete_count == 1


def test_unavailable_not_zero():
    r=compare_benchmark_sensitivity((obs('a', None, availability=E.UNAVAILABLE),), anchors(), (anchors('other', 1, 11, 21),))
    assert r.rows[0].max_absolute_shift is None


def test_empty_population():
    assert compare_benchmark_sensitivity((), anchors(), (anchors('other', 1, 11, 21),)).greatest_shift is None


def test_duplicate_army_rejected():
    with pytest.raises(ValueError, match='Duplicate'):
        compare_benchmark_sensitivity((obs('x',1),obs('x',2)), anchors(), (anchors('other'),))


def test_duplicate_benchmark_rejected():
    with pytest.raises(ValueError, match='identifiers'):
        compare_benchmark_sensitivity((obs('x',1),), anchors(), (anchors(),))


def test_metric_mismatch_rejected():
    with pytest.raises(ValueError, match='matching'):
        compare_benchmark_sensitivity((obs('x',1),), anchors(), (anchors('other',metric='shooting'),))


def test_unit_mismatch_rejected():
    with pytest.raises(ValueError, match='matching'):
        compare_benchmark_sensitivity((obs('x',1),), anchors(), (anchors('other',unit='other'),))


def test_measurement_unit_mismatch_rejected():
    entry=SensitivityObservation('x','Good','elite',measure(1,unit='other'))
    with pytest.raises(ValueError, match='Incompatible'):
        compare_benchmark_sensitivity((entry,), anchors(), (anchors('other'),))


def test_invalid_alignment_rejected():
    with pytest.raises(ValueError, match='Alignment'):
        obs('a', 1, alignment='Neutral')


def test_archetype_cohorts():
    assert {x.label for x in describe_cohorts(report())} == {'elite','shooting','infantry'}


def test_alignment_cohorts():
    g=describe_cohorts(report(),by='alignment')
    assert sum(x.count for x in g)==3


def test_cohort_with_missing_score():
    r=compare_benchmark_sensitivity((obs('a',None,availability=E.UNAVAILABLE),),anchors(),(anchors('other'),))
    assert describe_cohorts(r)[0].mean_candidate_score is None


def test_cohort_invalid_grouping():
    with pytest.raises(ValueError):
        describe_cohorts(report(),by='army_id')


def test_local_sensitivity_monotonic():
    a,b,c=local_score_sensitivity(measure(10),anchors(),1)
    assert a < b < c


def test_local_sensitivity_clips_at_endpoints():
    assert local_score_sensitivity(measure(0),anchors(),1)[0] == 0


def test_local_sensitivity_requires_complete_evidence():
    with pytest.raises(ValueError):
        local_score_sensitivity(measure(4,E.PARTIAL),anchors(),1)


def test_local_sensitivity_rejects_invalid_delta():
    with pytest.raises(ValueError):
        local_score_sensitivity(measure(4),anchors(),0)


def test_no_alternative_rejected():
    with pytest.raises(ValueError):
        compare_benchmark_sensitivity((obs('a',1),),anchors(),())
