"""DEV-077S-I2-I-B1: non-scoring unified calibration architecture.

No numerical benchmarks, normalisation functions, category cut-offs or
production scoring connections are approved by this module.
"""
from dataclasses import dataclass
from enum import Enum
from math import isfinite

from unified_capability_inventory import METRIC_NAMES
from unified_capability_overlap_audit import RISKS


class EvidenceAvailability(str, Enum):
    AVAILABLE = 'available'
    PARTIAL = 'partial'
    UNAVAILABLE = 'unavailable'


class CalibrationApproval(str, Enum):
    PROPOSED = 'proposed'
    APPROVED = 'approved'


@dataclass(frozen=True)
class RawMeasurement:
    """A metric-specific observation, not a calibrated capability score.

    `value=None` means no numerical observation; it is never a zero.
    An explicitly observed zero is valid when status is AVAILABLE or PARTIAL.
    """
    metric: str
    value: float | None
    unit: str
    population: str
    provenance: str
    availability: EvidenceAvailability
    assumptions: tuple[str, ...] = ()
    unresolved: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.metric not in METRIC_NAMES:
            raise ValueError('Unknown capability')
        if not isinstance(self.availability, EvidenceAvailability):
            raise TypeError('Invalid availability')
        if not all(isinstance(x, str) and x.strip() for x in
                   (self.unit, self.population, self.provenance)):
            raise ValueError('Unit, population and provenance are required')
        if self.value is None:
            if self.availability is EvidenceAvailability.AVAILABLE:
                raise ValueError('Available evidence requires a raw value')
        elif (isinstance(self.value, bool) or not isinstance(self.value, (int, float))
              or not isfinite(self.value)):
            raise ValueError('Raw value must be finite numeric or None')
        elif self.availability is EvidenceAvailability.UNAVAILABLE:
            raise ValueError('Unavailable evidence cannot contain a raw value')
        if (self.availability is EvidenceAvailability.PARTIAL and not self.unresolved):
            raise ValueError('Partial evidence must list unresolved conditions')


@dataclass(frozen=True)
class BenchmarkSpecification:
    """A proposed reference population and unit; not yet a fitted benchmark."""
    metric: str
    identifier: str
    target_population: str
    measurement_unit: str
    source: str
    reference_value: float | None = None
    approval: CalibrationApproval = CalibrationApproval.PROPOSED

    def __post_init__(self) -> None:
        if self.metric not in METRIC_NAMES:
            raise ValueError('Unknown capability')
        if not all(isinstance(x, str) and x.strip() for x in
                   (self.identifier, self.target_population, self.measurement_unit, self.source)):
            raise ValueError('Benchmark identity, population, unit and source required')
        if self.reference_value is not None and (isinstance(self.reference_value, bool)
              or not isinstance(self.reference_value, (int, float))
              or not isfinite(self.reference_value)):
            raise ValueError('Benchmark must be finite numeric or None')
        if self.approval is not CalibrationApproval.PROPOSED:
            raise ValueError('B1 cannot approve a benchmark')


@dataclass(frozen=True)
class CalibratedCapability:
    """Future output shape only; scoring computations are intentionally absent."""
    metric: str
    score: float | None
    availability: EvidenceAvailability
    benchmark_id: str | None
    calibration_version: str | None
    evidence_provenance: str
    unresolved: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.metric not in METRIC_NAMES:
            raise ValueError('Unknown capability')
        if self.score is not None:
            if (isinstance(self.score, bool) or not isinstance(self.score, (int, float))
                    or not isfinite(self.score) or not 0 <= self.score <= 1):
                raise ValueError('Calibrated score must be between 0 and 1')
            if self.availability is not EvidenceAvailability.AVAILABLE:
                raise ValueError('Incomplete evidence must not masquerade as a full score')
            if not self.benchmark_id or not self.calibration_version or not self.evidence_provenance:
                raise ValueError('Calibrated scores require traceable evidence and version')
        elif self.availability is EvidenceAvailability.AVAILABLE:
            raise ValueError('Available calibrated output requires a score')


@dataclass(frozen=True)
class CalibrationArchitecture:
    metrics: tuple[str, ...]
    pipeline: tuple[str, ...]
    safeguards: tuple[str, ...]
    reference_values_approved: bool = False
    rating_thresholds_approved: bool = False
    production_scoring_enabled: bool = False


def build_calibration_architecture() -> CalibrationArchitecture:
    return CalibrationArchitecture(
        metrics=METRIC_NAMES,
        pipeline=('raw_mechanical_evidence', 'verified_benchmark',
                  'normalised_capability', 'classified_dashboard_rating'),
        safeguards=('unavailable_is_not_zero', 'partial_is_not_fully_scored',
                    'version_calibration', 'preserve_raw_units',
                    'shared_resource_accounting', 'scenario_mapping_separate',
                    'retain_legacy_comparison', 'no_automatic_benchmark_selection'),
    )


def validate_calibration_architecture() -> None:
    architecture = build_calibration_architecture()
    if architecture.metrics != METRIC_NAMES or len(set(architecture.metrics)) != 10:
        raise ValueError('Missing or duplicate canonical metrics')
    if len(architecture.pipeline) != 4:
        raise ValueError('Invalid pipeline')
    if len(set(architecture.safeguards)) != len(architecture.safeguards):
        raise ValueError('Duplicate safeguard')
    if architecture.reference_values_approved or architecture.rating_thresholds_approved or architecture.production_scoring_enabled:
        raise ValueError('B1 must not activate calibration or scoring')
    if not RISKS:
        raise ValueError('Shared-evidence risks must be retained')
