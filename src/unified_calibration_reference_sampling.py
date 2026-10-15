"""DEV-077S-I2-I-B3: research-only reference-army sampling.

Observations must come from independent measured army runs. The registry below
is a sampling PLAN, not a collection of measured scores or approved anchors.
No production scoring, dashboard rating or scenario integration occurs here.
"""
from dataclasses import dataclass
from math import isfinite
from collections import Counter

from unified_capability_inventory import METRIC_NAMES
from unified_calibration_contract import RawMeasurement, EvidenceAvailability
from unified_calibration_benchmarks import ReferenceAnchors, propose_reference_anchors


@dataclass(frozen=True)
class ReferenceArmy:
    key: str
    label: str
    alignment: str
    archetype: str
    points_limit: int
    roster_source: str
    roster_revision: str

    def __post_init__(self):
        if not all(isinstance(x, str) and x.strip() for x in
                   (self.key, self.label, self.archetype, self.roster_source, self.roster_revision)):
            raise ValueError('Reference army identity and roster provenance required')
        if self.alignment not in ('Good', 'Evil'):
            raise ValueError('Alignment must be Good or Evil')
        if type(self.points_limit) is not int or self.points_limit <= 0:
            raise ValueError('Positive integer points limit required')


@dataclass(frozen=True)
class SampleObservation:
    army_key: str
    fixture_id: str
    benchmark_context: str
    measurement: RawMeasurement

    def __post_init__(self):
        if not all(isinstance(x, str) and x.strip() for x in
                   (self.army_key, self.fixture_id, self.benchmark_context)):
            raise ValueError('Sample identity and benchmark context required')


@dataclass(frozen=True)
class SampleCoverage:
    metric: str
    eligible_count: int
    partial_count: int
    unavailable_count: int
    distinct_armies: int
    alignment_count: int
    archetype_count: int
    candidate_ready: bool
    limitations: tuple[str, ...]
    anchors_approved: bool = False
    production_scoring_enabled: bool = False


# Explicit recruitment plan. Never present these rows as imported rosters.
REFERENCE_PLAN = (
    ('dol_guldur_elite', 'Dol Guldur', 'Evil', 'elite_magic'),
    ('evil_infantry', 'Evil infantry reference', 'Evil', 'infantry'),
    ('good_infantry', 'Good infantry reference', 'Good', 'infantry'),
    ('mirkwood_rangers', 'Mirkwood Rangers', 'Good', 'shooting'),
    ('evil_cavalry', 'Evil cavalry reference', 'Evil', 'cavalry'),
    ('good_cavalry', 'Good cavalry reference', 'Good', 'cavalry'),
)


def reference_army_plan(points_limit: int = 700) -> tuple[tuple[str, str, str, str, int], ...]:
    if type(points_limit) is not int or points_limit <= 0:
        raise ValueError('Invalid point limit')
    return tuple((*row, points_limit) for row in REFERENCE_PLAN)


def validate_reference_roster(armies: tuple[ReferenceArmy, ...]) -> None:
    if not isinstance(armies, tuple):
        raise TypeError('Armies must be a tuple')
    if any(not isinstance(a, ReferenceArmy) for a in armies):
        raise TypeError('Expected ReferenceArmy')
    keys = [a.key for a in armies]
    if len(keys) != len(set(keys)):
        raise ValueError('Duplicate reference-army identity')


def _checked_samples(armies, samples):
    validate_reference_roster(armies)
    if not isinstance(samples, tuple) or any(not isinstance(s, SampleObservation) for s in samples):
        raise TypeError('Samples must be SampleObservation tuple')
    lookup = {a.key: a for a in armies}
    seen = set()
    for s in samples:
        if s.army_key not in lookup:
            raise ValueError('Sample references unknown army')
        identity = (s.army_key, s.fixture_id, s.measurement.metric)
        if identity in seen:
            raise ValueError('Duplicate army/fixture/metric sample')
        seen.add(identity)
    return lookup


def sample_coverage(metric: str, armies: tuple[ReferenceArmy, ...],
                    samples: tuple[SampleObservation, ...], *, min_armies: int = 3,
                    require_both_alignments: bool = True) -> SampleCoverage:
    if metric not in METRIC_NAMES:
        raise ValueError('Unknown metric')
    if type(min_armies) is not int or min_armies < 3:
        raise ValueError('At least three independent armies required')
    lookup = _checked_samples(armies, samples)
    relevant = [s for s in samples if s.measurement.metric == metric]
    good = [s for s in relevant if s.measurement.availability is EvidenceAvailability.AVAILABLE]
    partial = sum(s.measurement.availability is EvidenceAvailability.PARTIAL for s in relevant)
    absent = sum(s.measurement.availability is EvidenceAvailability.UNAVAILABLE for s in relevant)
    ids = {s.army_key for s in good}
    alignments = {lookup[k].alignment for k in ids}
    archetypes = {lookup[k].archetype for k in ids}
    units = {(s.measurement.unit, s.measurement.population, s.benchmark_context) for s in good}
    limitations = []
    if len(ids) < min_armies:
        limitations.append('insufficient_independent_armies')
    if require_both_alignments and len(alignments) < 2:
        limitations.append('missing_good_or_evil')
    if len(archetypes) < 2:
        limitations.append('insufficient_archetype_diversity')
    if len(units) > 1:
        limitations.append('incompatible_unit_population_or_context')
    if len({s.measurement.value for s in good}) < 3:
        limitations.append('insufficient_distinct_observations')
    if partial or absent:
        limitations.append('incomplete_observations_excluded')
    return SampleCoverage(metric, len(good), partial, absent, len(ids),
                          len(alignments), len(archetypes),
                          not any(x for x in limitations if x != 'incomplete_observations_excluded'),
                          tuple(limitations))


def candidate_anchors_from_samples(metric: str, identifier: str,
                                   armies: tuple[ReferenceArmy, ...],
                                   samples: tuple[SampleObservation, ...],
                                   *, min_armies: int = 3) -> ReferenceAnchors:
    coverage = sample_coverage(metric, armies, samples, min_armies=min_armies)
    if not coverage.candidate_ready:
        raise ValueError('Insufficient or incompatible reference coverage: ' + ', '.join(coverage.limitations))
    eligible = [s for s in samples if s.measurement.metric == metric
                and s.measurement.availability is EvidenceAvailability.AVAILABLE]
    # Repeated fixtures from one army cannot inflate the number of independent
    # reference armies: use one sample per army at this stage.
    if len({s.army_key for s in eligible}) != len(eligible):
        raise ValueError('One observation per independent army is required for candidate anchors')
    first = eligible[0].measurement
    return propose_reference_anchors(
        metric=metric, identifier=identifier, unit=first.unit,
        population=first.population,
        provenance='B3 candidate: ' + '; '.join(sorted(s.army_key + '/' + s.fixture_id for s in eligible)),
        observations=tuple(s.measurement.value for s in eligible),
    )
