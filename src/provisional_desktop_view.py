"""I2-I-P2-B: display-only provisional capability view adapter.

This module does not import scoring, scenarios or optimiser services.
Never substitute legacy metric assessment values for mechanical readings.
"""
from __future__ import annotations

from pathlib import Path
from collections.abc import Mapping

from provisional_calibration import load_reference, rate_capabilities, EVALUATED, CONDITIONAL, NOT_EVALUATED

REFERENCE_PATH = Path(__file__).resolve().parent.parent / 'data' / 'calibration' / 'provisional_six_army_v2.json'
ORDER = (
    'offence_density', 'stationary_shooting', 'open_ground_mobility',
    'courage_reliability', 'army_survival_density', 'per_model_resilience',
    'magic', 'hero_hunting', 'control', 'command', 'objective',
)
LABELS = {
    'offence_density': 'Offence Density',
    'stationary_shooting': 'Stationary Shooting',
    'open_ground_mobility': 'Open-Ground Mobility',
    'courage_reliability': 'Courage Reliability',
    'army_survival_density': 'Army Survival Density',
    'per_model_resilience': 'Per-Model Resilience',
    'magic': 'Magic', 'hero_hunting': 'Hero Hunting',
    'control': 'Control', 'command': 'Command', 'objective': 'Objective',
}


def build_provisional_desktop_view(
    defence: dict | None,
    *,
    qualified_measurements: Mapping[str, float | None] | None = None,
    evidence_statuses: Mapping[str, str] | None = None,
    reference_path: str | Path = REFERENCE_PATH,
) -> dict:
    """Build a presentation DTO from explicit, separately qualified evidence.

    `qualified_measurements` must be mechanical raw measurements matching the
    exact frozen benchmark; it must never be populated from legacy ratings.
    Unprovided metrics are Not evaluated, rather than a numeric zero.
    """
    reference = load_reference(reference_path)
    values = dict(qualified_measurements or {})
    statuses = {name: NOT_EVALUATED for name in ORDER}
    statuses.update(evidence_statuses or {})
    if defence is not None:
        for name in ('army_survival_density', 'per_model_resilience'):
            reading = defence[name]
            if reading.get('calibrated') is not False:
                raise ValueError('Defence mechanical measurement must be raw and uncalibrated')
            if name in values and values[name] != reading['value']:
                raise ValueError('Conflicting Defence measurements')
            values[name] = reading['value']
            statuses[name] = EVALUATED
    for name in qualified_measurements or {}:
        if name not in (evidence_statuses or {}) and name not in ('army_survival_density','per_model_resilience'):
            # Explicit values alone do not prove benchmark qualification.
            statuses[name] = NOT_EVALUATED
    ratings = rate_capabilities(values, reference, evidence_statuses=statuses)
    rows = []
    for key in ORDER:
        rating = ratings[key]
        rows.append({**rating.as_dict(), 'label': LABELS[key]})
    return {
        'title': 'PROVISIONAL — SIX-ARMY REFERENCE',
        'explanation': reference['scale_meaning'],
        'reference_version': reference['reference_version'],
        'display_only': True,
        'production_scoring_changed': False,
        'defence_independent_composite_weighting_allowed': False,
        'metrics': tuple(rows),
    }


def build_provisional_summary(panel: dict) -> str:
    """Plain-text preview. A later Tkinter surface can display these rows."""
    lines = [panel['title'], '0 = no measured output; 1 = frozen six-army maximum (not an MESBG limit)']
    for row in panel['metrics']:
        value = row['rating']
        if value is None:
            lines.append(f"{row['label']}: {'Conditional — Not evaluated' if row['status'] == CONDITIONAL else 'Not evaluated'}")
            continue
        filled = max(0, min(20, round(value * 20)))
        bar = '█' * filled + '░' * (20 - filled)
        clip = ' [clipped]' if row['clipped'] else ''
        lines.append(f"{row['label']:<23} {bar} {value:.3f} (raw {row['raw_value']:.3f} {row['unit']}){clip}")
    lines.append('Presentation only — scenario and optimiser results unchanged')
    return '\n'.join(lines)
