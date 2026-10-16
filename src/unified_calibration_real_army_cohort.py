"""DEV-077S-I2-I-C3: read-only real-army calibration evidence cohort.

Consumes C1/C2 measurement snapshots generated from verified army analysis.
Does not load rosters, invent measurements, approve anchors, or alter scoring.
"""
from dataclasses import dataclass
from unified_capability_inventory import METRIC_NAMES
from unified_calibration_contract import EvidenceAvailability
from unified_calibration_reference_sampling import (
    ReferenceArmy, SampleObservation, sample_coverage,
    candidate_anchors_from_samples,
)
from unified_real_army_measurements import MechanicalArmySnapshot


@dataclass(frozen=True)
class VerifiedArmyRun:
    """Explicitly identifies a real, reproducible roster analysis run."""
    reference: ReferenceArmy
    snapshot: MechanicalArmySnapshot
    roster_file: str
    roster_sha256: str
    analysis_commit: str
    benchmark_context: str

    def __post_init__(self):
        if not isinstance(self.reference, ReferenceArmy):
            raise TypeError("reference must be ReferenceArmy")
        if not isinstance(self.snapshot, MechanicalArmySnapshot):
            raise TypeError("snapshot must be MechanicalArmySnapshot")
        for field in ("roster_file", "roster_sha256", "analysis_commit", "benchmark_context"):
            x = getattr(self, field)
            if not isinstance(x, str) or not x.strip():
                raise ValueError(f"{field} provenance required")
        if len(self.roster_sha256) != 64 or any(c not in "0123456789abcdef" for c in self.roster_sha256.lower()):
            raise ValueError("roster_sha256 must be a SHA-256 hex digest")
        if self.snapshot.army_key != self.reference.key:
            raise ValueError("snapshot and reference army identities differ")
        if self.snapshot.source_commit != self.analysis_commit:
            raise ValueError("snapshot commit differs from analysis commit")
        if self.snapshot.production_scoring_enabled:
            raise ValueError("C3 must not activate scoring")
        if tuple(m.metric for m in self.snapshot.measurements) != METRIC_NAMES:
            raise ValueError("snapshot must contain ten metrics in canonical order")
        if self.snapshot.available_count != sum(
            m.availability is EvidenceAvailability.AVAILABLE
            for m in self.snapshot.measurements
        ):
            raise ValueError("snapshot available_count inconsistent")
        if self.snapshot.unresolved_metrics != tuple(
            m.metric for m in self.snapshot.measurements
            if m.availability is not EvidenceAvailability.AVAILABLE
        ):
            raise ValueError("snapshot unresolved_metrics inconsistent")


@dataclass(frozen=True)
class CohortMetricReport:
    metric: str
    complete_armies: int
    partial_observations: int
    unavailable_observations: int
    population_compatible: bool
    candidate_ready: bool
    blockers: tuple[str, ...]
    candidate_anchors: object | None = None
    anchors_approved: bool = False


@dataclass(frozen=True)
class CohortReport:
    army_count: int
    source_commit: str | None
    metric_reports: tuple[CohortMetricReport, ...]
    production_scoring_enabled: bool = False


def collect_cohort(runs: tuple[VerifiedArmyRun, ...], *, min_armies: int = 3) -> CohortReport:
    """Assess independently documented runs; anchors remain proposed.

    One roster/run per reference army prevents pseudo-replication. Sample
    compatibility is evaluated separately for each capability metric.
    """
    if not isinstance(runs, tuple) or any(not isinstance(r, VerifiedArmyRun) for r in runs):
        raise TypeError("runs must be tuple[VerifiedArmyRun, ...]")
    if type(min_armies) is not int or min_armies < 3:
        raise ValueError("min_armies must be >= 3")
    keys = [r.reference.key for r in runs]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate independent reference army")
    commits = {r.analysis_commit for r in runs}
    if len(commits) > 1:
        raise ValueError("mixed analysis commits cannot form a calibration cohort")
    armies = tuple(r.reference for r in runs)
    samples = tuple(
        SampleObservation(r.reference.key, r.snapshot.fixture_id,
                          r.benchmark_context, m)
        for r in runs for m in r.snapshot.measurements
    )
    reports = []
    for metric in METRIC_NAMES:
        coverage = sample_coverage(metric, armies, samples, min_armies=min_armies)
        compatible = "incompatible_unit_population_or_context" not in coverage.limitations
        anchor = None
        blockers = list(coverage.limitations)
        if coverage.candidate_ready:
            try:
                anchor = candidate_anchors_from_samples(
                    metric, f"i2i-c3-{metric}-candidate", armies, samples,
                    min_armies=min_armies,
                )
            except ValueError as exc:
                blockers.append(f"candidate_rejected:{exc}")
        reports.append(CohortMetricReport(
            metric=metric,
            complete_armies=coverage.distinct_armies,
            partial_observations=coverage.partial_count,
            unavailable_observations=coverage.unavailable_count,
            population_compatible=compatible,
            candidate_ready=anchor is not None,
            blockers=tuple(blockers),
            candidate_anchors=anchor,
        ))
    return CohortReport(len(runs), next(iter(commits)) if commits else None,
                        tuple(reports))


def cohort_report_rows(report: CohortReport) -> tuple[dict, ...]:
    """Flat, serialisable research results; no inferred production ratings."""
    if not isinstance(report, CohortReport):
        raise TypeError("report must be CohortReport")
    return tuple({
        "metric": item.metric,
        "complete_armies": item.complete_armies,
        "partial_observations": item.partial_observations,
        "unavailable_observations": item.unavailable_observations,
        "population_compatible": item.population_compatible,
        "candidate_ready": item.candidate_ready,
        "blockers": ";".join(item.blockers),
        "anchors_approved": False,
    } for item in report.metric_reports)
