"""C3 cohort tests use synthetic fixtures, never represented as measured armies."""
from dataclasses import replace
from hashlib import sha256
import pytest

from unified_capability_inventory import METRIC_NAMES
from unified_calibration_contract import RawMeasurement, EvidenceAvailability
from unified_calibration_reference_sampling import ReferenceArmy
from unified_real_army_measurements import MechanicalArmySnapshot
from unified_calibration_real_army_cohort import (
    VerifiedArmyRun, collect_cohort, cohort_report_rows,
)

COMMIT = "b2d1132"
DIGEST = sha256(b"fixture-bytes").hexdigest()


def make_run(key, alignment="Evil", archetype="infantry", value=1.0,
             *, status=EvidenceAvailability.AVAILABLE, unit="output_density",
             context="benchmark-v1"):
    ref = ReferenceArmy(key, key, alignment, archetype, 700,
                        f"fixtures/{key}.json", "test-revision")
    measurements = []
    for metric in METRIC_NAMES:
        availability = status if metric == "offence" else EvidenceAvailability.UNAVAILABLE
        measurements.append(RawMeasurement(
            metric, float(value) if availability is EvidenceAvailability.AVAILABLE else None,
            unit if metric == "offence" else "unverified",
            "configured reference army" if metric == "offence" else "unknown",
            f"synthetic/{key}",
            availability,
            unresolved=() if availability is EvidenceAvailability.AVAILABLE
            else ("awaiting_real_provider_evidence",),
        ))
    snap = MechanicalArmySnapshot(
        key, f"fixture-{key}", COMMIT, tuple(measurements),
        int(status is EvidenceAvailability.AVAILABLE),
        tuple(m.metric for m in measurements
              if m.availability is not EvidenceAvailability.AVAILABLE),
    )
    return VerifiedArmyRun(ref, snap, f"fixtures/{key}.json", DIGEST,
                           COMMIT, context)


def cohort():
    return (make_run("a", "Evil", "elite", 1.0),
            make_run("b", "Good", "infantry", 2.0),
            make_run("c", "Evil", "cavalry", 3.0))


def test_empty_is_non_scoring():
    report = collect_cohort(())
    assert report.army_count == 0
    assert all(not r.candidate_ready for r in report.metric_reports)
    assert report.production_scoring_enabled is False


def test_candidate_proposed_when_independent_compatible():
    report = collect_cohort(cohort())
    offence = report.metric_reports[0]
    assert offence.candidate_ready
    assert offence.candidate_anchors.low == 1.0
    assert offence.candidate_anchors.typical == 2.0
    assert offence.candidate_anchors.high == 3.0
    assert offence.anchors_approved is False


def test_missing_other_metrics_not_zero():
    report = collect_cohort(cohort())
    assert len(report.metric_reports) == 10
    for item in report.metric_reports[1:]:
        assert not item.candidate_ready
        assert item.unavailable_observations == 3


def test_mixed_population_context_rejected():
    runs = cohort()
    report = collect_cohort((*runs[:2],
        replace(runs[2], benchmark_context="different")))
    assert not report.metric_reports[0].candidate_ready
    assert not report.metric_reports[0].population_compatible


def test_missing_alignment_rejected():
    runs = tuple(make_run(str(i), "Evil", str(i), float(i)) for i in range(3))
    assert not collect_cohort(runs).metric_reports[0].candidate_ready


def test_duplicate_army_rejected():
    with pytest.raises(ValueError, match="duplicate independent"):
        collect_cohort((cohort()[0], cohort()[0]))


def test_mixed_commits_rejected():
    runs = cohort()
    bad = replace(runs[2], analysis_commit="changed",
                  snapshot=replace(runs[2].snapshot, source_commit="changed"))
    with pytest.raises(ValueError, match="mixed analysis"):
        collect_cohort((*runs[:2], bad))


def test_sha256_required():
    with pytest.raises(ValueError, match="SHA-256"):
        replace(cohort()[0], roster_sha256="not-a-hash")


def test_snapshot_identity_must_match():
    with pytest.raises(ValueError, match="identities"):
        replace(cohort()[0], snapshot=replace(cohort()[0].snapshot,
                                              army_key="other"))


def test_snapshot_commit_must_match():
    with pytest.raises(ValueError, match="commit differs"):
        replace(cohort()[0], analysis_commit="different")


def test_no_activated_scoring():
    with pytest.raises(ValueError, match="activate scoring"):
        replace(cohort()[0], snapshot=replace(cohort()[0].snapshot,
                                             production_scoring_enabled=True))


def test_minimum_three_armies():
    assert not collect_cohort(cohort()[:2]).metric_reports[0].candidate_ready


def test_nonidentical_metric_population():
    runs = cohort()
    changed = list(runs[2].snapshot.measurements)
    changed[0] = replace(changed[0], population="different")
    altered = replace(runs[2], snapshot=replace(runs[2].snapshot,
                                               measurements=tuple(changed)))
    assert not collect_cohort((*runs[:2], altered)).metric_reports[0].candidate_ready


def test_flat_rows_do_not_offer_score():
    rows = cohort_report_rows(collect_cohort(cohort()))
    assert len(rows) == 10
    assert set(rows[0]) == {"metric", "complete_armies", "partial_observations",
                           "unavailable_observations", "population_compatible",
                           "candidate_ready", "blockers", "anchors_approved"}
    assert rows[0]["anchors_approved"] is False


@pytest.mark.parametrize("metric", METRIC_NAMES)
def test_canonical_metric_order(metric):
    assert metric in [r.metric for r in collect_cohort(cohort()).metric_reports]
