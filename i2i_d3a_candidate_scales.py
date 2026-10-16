"""I2-I-D3-A: read-only comparison of illustrative six-army display scales.

NOT a calibration fit or a recommendation to use cohort extrema as anchors.
All transformations are within-metric only; no composite score is calculated.
"""
from __future__ import annotations

import json
from math import isfinite
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent
METRIC_KEYS = {
    'offence_density': ('offence',),
    'army_survival_density': ('defence',),
    'per_model_resilience': (),
    'open_ground_mobility': ('mobility',),
    'stationary_shooting': ('shooting',),
    'courage_reliability': ('courage',),
}


def read_json(path: Path) -> dict:
    data = path.read_bytes()
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return json.loads(data.decode('utf-16'))
    if b'\x00' in data[:4]:
        return json.loads(data.decode('utf-16-le'))
    return json.loads(data.decode('utf-8-sig'))


def gated(d1, d2c, b8c) -> bool:
    return (
        d1.get('stage') == 'I2-I-D1' and d1.get('status') == 'matrix_complete'
        and d2c.get('stage') == 'I2-I-D2-C'
        and d2c.get('status') == 'cross_metric_audit_complete'
        and d2c.get('errors') == []
        and b8c.get('stage') == 'B8-C'
        and b8c.get('status') == 'provisional_evidence_qualified'
        and b8c.get('provisional_references') == 6
        and all(x.get('calibration_anchors_approved') is False for x in (d1,d2c,b8c))
        and all(x.get('numerical_calibration_permitted') is False for x in (d1,d2c,b8c))
    )


def percentile_positions(values: list[float]) -> list[float]:
    """Tie-aware midrank percentile; single-element spread is undefined."""
    if len(values) < 2:
        raise ValueError('at least two reference points required')
    ordered = sorted(values)
    return [((ordered.index(v) + (len(ordered) - 1 - ordered[::-1].index(v))) / 2)
            / (len(values) - 1) for v in values]


def transformations(values: list[float]) -> dict:
    if len(values) < 2 or any(not isfinite(v) for v in values):
        raise ValueError('requires finite measurements across at least two armies')
    lo, hi = min(values), max(values)
    med = median(values)
    if lo == hi:
        return {'minmax': None, 'midrank': None, 'median_ratio': None,
                'limitation': 'no variation; avoid a fabricated score'}
    if med <= 0:
        med_ratios = None
    else:
        med_ratios = [v / med for v in values]
    return {
        'minmax': [(v - lo) / (hi - lo) for v in values],
        'midrank': percentile_positions(values),
        'median_ratio': med_ratios,
        'limitation': None,
    }


def build_report(d1: dict, d2c: dict, b8c: dict) -> dict:
    base = {'stage': 'I2-I-D3-A', 'calibration_anchors_approved': False,
            'numerical_calibration_permitted': False,
            'production_scoring_modified': False,
            'composite_score_calculated': False}
    if not gated(d1, d2c, b8c):
        return {**base, 'status': 'blocked_by_evidence_gate', 'scales': {}}
    rows = d1.get('rows', [])
    if (len(rows) != 6 or len({r.get('army') for r in rows}) != 6
            or any(r.get('issues') for r in rows)):
        return {**base, 'status': 'blocked_incomplete_measurements', 'scales': {}}
    names = [r['army'] for r in rows]
    reference_names = {r.get('army') for r in b8c.get('armies', [])
                       if r.get('candidate_status') == 'provisional_reference'}
    if set(names) != reference_names or len(reference_names) != 6:
        return {**base, 'status': 'blocked_reference_mismatch', 'scales': {}}
    outcomes = {}
    for key, (d1key,) in ((k,v) for k,v in METRIC_KEYS.items() if v):
        try:
            nums = [float(r['measurements'][d1key]['value']) for r in rows]
            if not all(isfinite(v) for v in nums):
                raise ValueError('nonfinite')
        except (KeyError, TypeError, ValueError) as ex:
            return {**base,'status': 'blocked_incomplete_measurements',
                    'reason': f'{key}: {ex}', 'scales': {}}
        outcomes[key] = {'raw_values': dict(zip(names, nums)),
                         'illustrative_transforms': {
                             k: None if v is None else dict(zip(names, v))
                             for k,v in transformations(nums).items() if k != 'limitation'},
                         'minimum': min(nums), 'maximum': max(nums),
                         'median': median(nums)}
    # The D2-C report already contains independently derived per-model values and
    # explicitly records the dependency. Extract them from D2-A evidence instead
    # of silently manufacturing or independently fitting a second Defence axis.
    defence = outcomes['army_survival_density']['raw_values']
    model_counts = {r['army']: next((b['models'] for b in b8c['armies']
                                      if b['army']==r['army']), None) for r in rows}
    points = {r['army']: next((b['points'] for b in b8c['armies']
                               if b['army']==r['army']), None) for r in rows}
    if any(not isinstance(model_counts[n], int) or model_counts[n] <= 0
           or not isinstance(points[n], int) or points[n] <= 0 for n in names):
        return {**base,'status':'blocked_reference_counts', 'scales':{}}
    resilience = [defence[n] * points[n] / (100 * model_counts[n]) for n in names]
    outcomes['per_model_resilience'] = {
        'raw_values': dict(zip(names, resilience)),
        'illustrative_transforms': {
            k: None if v is None else dict(zip(names,v))
            for k,v in transformations(resilience).items() if k != 'limitation'},
        'minimum': min(resilience), 'maximum': max(resilience),
        'median': median(resilience),
        'dependency': 'derived exactly from survival density, army points and model count',
    }
    # Test against the D2-C diagnostic rankings without re-approving archetypes.
    for metric, record in outcomes.items():
        expected = d2c['rankings'].get(metric)
        ranked = sorted(names, key=lambda n: (-record['raw_values'][n], n))
        if expected != ranked:
            return {**base,'status':'blocked_ranking_disagreement',
                    'reason':metric,'scales':{}}
    return {**base, 'status': 'illustrative_scales_complete', 'armies': names,
            'scales': outcomes,
            'methods': {
                'minmax': '0..1 within these six armies ONLY; forced extremes, unstable on adding armies',
                'midrank': 'tie-aware empirical rank positions; ignores magnitude of differences',
                'median_ratio': 'value / cohort median; not bounded 0..1 and not a rating',
            },
            'decision': 'no method approved; compare behaviour, do not select anchors',
            'double_counting_rule': 'survival density and resilience cannot enter as independent weighted metrics',
            'exclusions': ['Magic, Control, Command, Objective and Hero Hunting not assigned zero',
                           'Woodland Creature terrain and Iron Hills Chariot physical behaviour unresolved',
                           'Independent archetype and full rulebook completeness approval pending',
                           'Six nonrepresentative army lists cannot justify population thresholds']}


def main():
    required = {'d1':ROOT/'i2i_d1_measurement_matrix.json',
                'd2c':ROOT/'i2i_d2c_cross_metric_archetype_report.json',
                'b8c':ROOT/'b8c_reference_qualification.json'}
    missing = [p.name for p in required.values() if not p.exists()]
    if missing:
        print(json.dumps({'stage':'I2-I-D3-A','status':'missing_inputs',
                          'required_files':missing},indent=2))
        raise SystemExit(2)
    print(json.dumps(build_report(*(read_json(p) for p in required.values())),indent=2))

if __name__ == '__main__':
    main()
