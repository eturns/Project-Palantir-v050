"""DEV-077S-I2-I-B4: diagnostic-only sensitivity and composition checks.

No fairness verdict, real-army claim, approved reference or production score.
All inputs are explicitly supplied research observations. Scores remain B2
candidates; robustness metrics are descriptive, not certification thresholds.
"""
from dataclasses import dataclass
from math import isfinite
from statistics import mean

from unified_calibration_benchmarks import ReferenceAnchors, normalise_candidate
from unified_calibration_contract import RawMeasurement, EvidenceAvailability


@dataclass(frozen=True)
class SensitivityObservation:
    army_id: str
    alignment: str
    archetype: str
    measurement: RawMeasurement

    def __post_init__(self):
        if not isinstance(self.army_id, str) or not self.army_id.strip():
            raise ValueError('Unique army identity required')
        if self.alignment not in ('Good', 'Evil'):
            raise ValueError('Alignment must be Good or Evil')
        if not isinstance(self.archetype, str) or not self.archetype.strip():
            raise ValueError('Archetype is required')
        if not isinstance(self.measurement, RawMeasurement):
            raise TypeError('Expected RawMeasurement')


@dataclass(frozen=True)
class SensitivityRow:
    army_id: str
    alignment: str
    archetype: str
    raw_value: float | None
    base_score: float | None
    alternative_scores: tuple[float | None, ...]
    max_absolute_shift: float | None
    status: str


@dataclass(frozen=True)
class SensitivityReport:
    metric: str
    baseline_id: str
    alternative_ids: tuple[str, ...]
    rows: tuple[SensitivityRow, ...]
    paired_count: int
    incomplete_count: int
    greatest_shift: float | None
    mean_shift: float | None
    ranking_reversals: int
    evaluated_pairs: int
    production_scoring_enabled: bool = False
    benchmarks_approved: bool = False
    fairness_certified: bool = False


def _validate(observations, baseline, alternatives):
    if not isinstance(baseline, ReferenceAnchors):
        raise TypeError('Baseline must be ReferenceAnchors')
    if not isinstance(observations, tuple) or any(not isinstance(o, SensitivityObservation) for o in observations):
        raise TypeError('Observations must be SensitivityObservation tuple')
    if not isinstance(alternatives, tuple) or not alternatives or any(not isinstance(a, ReferenceAnchors) for a in alternatives):
        raise ValueError('At least one alternative ReferenceAnchors is required')
    ids = (baseline.identifier,) + tuple(a.identifier for a in alternatives)
    if len(set(ids)) != len(ids):
        raise ValueError('Benchmark identifiers must be unique')
    for anchor in alternatives:
        if (anchor.metric, anchor.unit, anchor.population) != (baseline.metric, baseline.unit, baseline.population):
            raise ValueError('All benchmark versions must use matching metric, unit and population')
    army_ids = [o.army_id for o in observations]
    if len(set(army_ids)) != len(army_ids):
        raise ValueError('Duplicate army identity')
    for o in observations:
        if (o.measurement.metric, o.measurement.unit, o.measurement.population) != (baseline.metric, baseline.unit, baseline.population):
            raise ValueError('Incompatible measurement context')


def compare_benchmark_sensitivity(observations: tuple[SensitivityObservation, ...],
                                  baseline: ReferenceAnchors,
                                  alternatives: tuple[ReferenceAnchors, ...]) -> SensitivityReport:
    """Evaluate score drift under alternative anchors without approving any score.

    A ranking reversal counts only *strict* pairwise sign reversals, not ties.
    A monotonic transformation using the same observations cannot reverse
    strict order unless saturation/ties intervene; ties are tracked separately
    by users of the row scores rather than misrepresented as reversals.
    """
    _validate(observations, baseline, alternatives)
    rows = []
    changes = []
    for o in observations:
        base = normalise_candidate(o.measurement, baseline)
        alts = tuple(normalise_candidate(o.measurement, a) for a in alternatives)
        other = tuple(a.candidate_score for a in alts)
        score = base.candidate_score
        shift = max((abs(score - v) for v in other), default=None) if score is not None and all(v is not None for v in other) else None
        if shift is not None:
            changes.append(shift)
        rows.append(SensitivityRow(o.army_id, o.alignment, o.archetype, o.measurement.value,
                                   score, other, shift, 'paired' if shift is not None else 'incomplete_evidence'))
    reversals = 0
    evaluated = 0
    for i, a in enumerate(rows):
        for b in rows[i+1:]:
            if a.base_score is None or b.base_score is None or any(x is None for x in a.alternative_scores + b.alternative_scores):
                continue
            evaluated += 1
            original = a.base_score - b.base_score
            if any(original * (x-y) < 0 for x, y in zip(a.alternative_scores, b.alternative_scores)):
                reversals += 1
    return SensitivityReport(baseline.metric, baseline.identifier, tuple(a.identifier for a in alternatives),
                             tuple(rows), len(changes), len(rows)-len(changes),
                             max(changes) if changes else None, mean(changes) if changes else None,
                             reversals, evaluated)


@dataclass(frozen=True)
class CohortSummary:
    label: str
    count: int
    mean_candidate_score: float | None
    min_candidate_score: float | None
    max_candidate_score: float | None
    evidence_missing: int


def describe_cohorts(report: SensitivityReport, *, by: str = 'archetype') -> tuple[CohortSummary, ...]:
    """Describe groups; unequal means are NOT evidence of unfair calibration."""
    if not isinstance(report, SensitivityReport):
        raise TypeError('Expected SensitivityReport')
    if by not in ('alignment', 'archetype'):
        raise ValueError('Group by alignment or archetype')
    labels = sorted({getattr(r, by) for r in report.rows})
    result = []
    for label in labels:
        group = [r for r in report.rows if getattr(r, by) == label]
        available = [r.base_score for r in group if r.base_score is not None]
        result.append(CohortSummary(label, len(group), mean(available) if available else None,
                                    min(available) if available else None, max(available) if available else None,
                                    len(group)-len(available)))
    return tuple(result)


def local_score_sensitivity(measurement: RawMeasurement, anchors: ReferenceAnchors,
                            delta: float) -> tuple[float, float, float]:
    """Candidate scores at x-delta, x, x+delta for an available observation."""
    if isinstance(delta, bool) or not isinstance(delta, (int, float)) or not isfinite(delta) or delta <= 0:
        raise ValueError('Delta must be a finite positive number')
    if measurement.availability is not EvidenceAvailability.AVAILABLE:
        raise ValueError('Local sensitivity requires complete evidence')
    results = []
    for x in (measurement.value-delta, measurement.value, measurement.value+delta):
        perturbed = RawMeasurement(measurement.metric, x, measurement.unit, measurement.population,
                                   measurement.provenance, EvidenceAvailability.AVAILABLE,
                                   measurement.assumptions)
        results.append(normalise_candidate(perturbed, anchors).candidate_score)
    return tuple(results)
