"""DEV-077S-I2-I-B2: candidate reference benchmarks and mathematics.

Research-only. No reference values or rating cut-offs are approved, and this
module must not be invoked by production scoring. Anchors are externally
supplied observations, not inferred from an army's own result.
"""
from dataclasses import dataclass
from math import isfinite

from unified_capability_inventory import METRIC_NAMES
from unified_calibration_contract import (
    RawMeasurement, EvidenceAvailability, CalibrationApproval,
)

CANDIDATE_VERSION = 'i2i-b2-candidate-v1'


@dataclass(frozen=True)
class ReferenceAnchors:
    """Three documented reference observations for a *single* measurement unit.

    low/typical/high represent independent reference points, not rating
    thresholds. A higher observation must mean better capability; reverse any
    inverse-direction metric in its mechanical adapter BEFORE calibration.
    """
    metric: str
    identifier: str
    unit: str
    population: str
    provenance: str
    low: float
    typical: float
    high: float
    approval: CalibrationApproval = CalibrationApproval.PROPOSED

    def __post_init__(self):
        if self.metric not in METRIC_NAMES:
            raise ValueError('Unknown metric')
        if any(not isinstance(s, str) or not s.strip() for s in
               (self.identifier, self.unit, self.population, self.provenance)):
            raise ValueError('Documented reference identity, unit and provenance required')
        for x in (self.low, self.typical, self.high):
            if isinstance(x, bool) or not isinstance(x, (float, int)) or not isfinite(x):
                raise ValueError('Reference anchors must be finite numbers')
        if not self.low < self.typical < self.high:
            raise ValueError('Reference anchors must be strictly increasing')
        if self.approval is not CalibrationApproval.PROPOSED:
            raise ValueError('B2 candidates cannot approve a benchmark')


@dataclass(frozen=True)
class CandidateNormalisation:
    metric: str
    raw_value: float | None
    candidate_score: float | None
    benchmark_id: str | None
    version: str
    availability: EvidenceAvailability
    status: str
    unresolved: tuple[str, ...]
    production_score: None = None
    dashboard_rating: None = None
    scenario_score: None = None


def normalise_candidate(measurement: RawMeasurement, anchors: ReferenceAnchors | None) -> CandidateNormalisation:
    """Piecewise-linear candidate with typical=0.5 and endpoint clipping.

    Scores are produced ONLY for fully available observations with a supplied
    unit/population-compatible reference. Never writes CalibratedCapability.
    """
    if not isinstance(measurement, RawMeasurement):
        raise TypeError('Expected RawMeasurement')
    if anchors is not None and not isinstance(anchors, ReferenceAnchors):
        raise TypeError('Expected ReferenceAnchors or None')
    status = 'candidate_only'
    score = None
    if measurement.availability is not EvidenceAvailability.AVAILABLE:
        status = 'incomplete_evidence'
    elif anchors is None:
        status = 'missing_reference'
    elif measurement.metric != anchors.metric:
        raise ValueError('Metric mismatch')
    elif measurement.unit != anchors.unit or measurement.population != anchors.population:
        raise ValueError('Unit or population mismatch')
    else:
        x = measurement.value
        if x <= anchors.low:
            score = 0.0
        elif x >= anchors.high:
            score = 1.0
        elif x <= anchors.typical:
            score = 0.5 * (x - anchors.low) / (anchors.typical - anchors.low)
        else:
            score = 0.5 + 0.5 * (x - anchors.typical) / (anchors.high - anchors.typical)
    return CandidateNormalisation(
        metric=measurement.metric,
        raw_value=measurement.value,
        candidate_score=score,
        benchmark_id=anchors.identifier if anchors is not None else None,
        version=CANDIDATE_VERSION,
        availability=measurement.availability,
        status=status,
        unresolved=measurement.unresolved,
    )


def propose_reference_anchors(
    *, metric: str, identifier: str, unit: str, population: str,
    provenance: str, observations: tuple[float, ...],
) -> ReferenceAnchors:
    """Describe observed low/median/high, requiring 3+ distinct observations.

    This is descriptive only. Whether the sample represents realistic army
    strength, book coverage, factions and point levels requires human review.
    Endpoints are observed extrema, *not* authoritative game-wide limits.
    """
    if not isinstance(observations, tuple) or len(observations) < 3:
        raise ValueError('At least three independent observations required')
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not isfinite(x)
           for x in observations):
        raise ValueError('All observations must be finite numbers')
    ordered = sorted(observations)
    mid = len(ordered) // 2
    median = (ordered[mid] if len(ordered) % 2 else
              (ordered[mid - 1] + ordered[mid]) / 2)
    return ReferenceAnchors(metric, identifier, unit, population, provenance,
                            ordered[0], median, ordered[-1])
