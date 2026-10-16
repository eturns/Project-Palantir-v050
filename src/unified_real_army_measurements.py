"""DEV-077S-I2-I-C1: read-only extraction of verified mechanical army measurements.

This module never changes ratings or scenario scores. Unknown measurements stay
unavailable, never zero. Source: Project-Palantir-v050 @ b2d1132.

The initial adapter supports offence and Defence from the established army
analysis result, and optional raw Shooting from an independently obtained
shooting-output-density observation. Other mechanical contracts require
metric-specific extraction audits before numerical activation.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Mapping

from unified_capability_inventory import METRIC_NAMES
from unified_calibration_contract import RawMeasurement, EvidenceAvailability


@dataclass(frozen=True)
class MechanicalArmySnapshot:
    army_key: str
    fixture_id: str
    source_commit: str
    measurements: tuple[RawMeasurement, ...]
    available_count: int
    unresolved_metrics: tuple[str, ...]
    production_scoring_enabled: bool = False


def _finite(value):
    return type(value) in (int, float) and isfinite(value)


def _measurement(metric, value, unit, population, provenance, *, issue=None):
    available = issue is None and _finite(value)
    return RawMeasurement(
        metric=metric,
        value=float(value) if available else None,
        unit=unit,
        population=population,
        provenance=provenance,
        availability=(EvidenceAvailability.AVAILABLE if available
                      else EvidenceAvailability.UNAVAILABLE),
        unresolved=(issue or 'verified_numeric_extractor_not_yet_connected',) if not available else (),
    )


def extract_mechanical_army_snapshot(
    *,
    army_key: str,
    fixture_id: str,
    analysis: Mapping,
    source_commit: str = 'b2d1132',
    raw_shooting_output_density: float | None = None,
) -> MechanicalArmySnapshot:
    """Extract available evidence from a real ``analyse_imported_army`` result.

    ``raw_shooting_output_density`` must originate from
    ``calculate_army_shooting_output_density`` using a documented defender;
    the dashboard Shooting assessment is already normalised and is rejected
    as a raw observation. The caller is responsible for real-roster provenance.
    """
    if not all(isinstance(x, str) and x.strip() for x in
               (army_key, fixture_id, source_commit)):
        raise ValueError('Army identity, fixture ID, and source commit are required')
    if not isinstance(analysis, Mapping):
        raise TypeError('analysis must be a mapping')
    if raw_shooting_output_density is not None and not _finite(raw_shooting_output_density):
        raise ValueError('Raw shooting density must be finite numeric or None')
    assessments = analysis.get('metric_assessments', ()) or ()
    by_metric = {}
    for entry in assessments:
        name = getattr(entry, 'metric', None)
        if name in by_metric:
            raise ValueError('Duplicate metric assessment')
        by_metric[name] = entry
    defence = analysis.get('mechanical_defence')
    if defence is not None and not isinstance(defence, Mapping):
        raise TypeError('mechanical_defence must be a mapping or None')
    defence = defence or {}
    results = []
    for metric in METRIC_NAMES:
        if metric == 'offence':
            assessment = by_metric.get(metric)
            value = getattr(assessment, 'value', None)
            results.append(_measurement(
                metric, value, 'offensive combat output per 100 army points',
                'configured army versus DEFAULT_COMBAT_BENCHMARK; charge_probability=1.0',
                'analyse_imported_army.metric_assessments.offence -> calculate_army_offensive_output_density',
                issue=None if _finite(value) else 'offence_assessment_missing_or_invalid',
            ))
        elif metric == 'defence':
            value = defence.get('combat_density')
            engagements = defence.get('engagements')
            valid = _finite(value) and type(engagements) is int and engagements >= 1
            results.append(_measurement(
                metric, value, 'defensive combat survival density per 100 army points',
                f'configured army versus DEFAULT_COMBAT_BENCHMARK; engagements={engagements}',
                'analyse_imported_army.mechanical_defence.combat_density',
                issue=None if valid else 'defence_density_or_engagements_missing',
            ))
        elif metric == 'shooting':
            results.append(_measurement(
                metric, raw_shooting_output_density,
                'shooting output density before provisional dashboard normalisation',
                'configured army versus build_shooting_benchmark_defender()',
                'calculate_army_shooting_output_density (caller-supplied raw observation)',
                issue=None if raw_shooting_output_density is not None
                else 'raw_shooting_density_not_provided_dashboard_score_is_normalised',
            ))
        else:
            results.append(_measurement(
                metric, None, 'metric-specific mechanical units pending audit',
                'configured army; reference context not yet approved',
                f'C1 awaiting verified extractor: {metric}',
            ))
    return MechanicalArmySnapshot(
        army_key=army_key, fixture_id=fixture_id, source_commit=source_commit,
        measurements=tuple(results),
        available_count=sum(m.availability is EvidenceAvailability.AVAILABLE for m in results),
        unresolved_metrics=tuple(m.metric for m in results
                                 if m.availability is not EvidenceAvailability.AVAILABLE),
    )
