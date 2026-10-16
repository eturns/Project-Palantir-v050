"""I2-I-D1 — read-only six-army mechanical measurements; no scoring or calibration."""
import json
import math
from pathlib import Path

from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from configured_profile import ConfiguredProfile
from profiles import Profile
from army_offence_capability import calculate_army_offensive_output_density
from mechanical_defence_diagnostics import calculate_mechanical_defence_diagnostics
from mobility_integration_contract import build_mobility_integration_contract
from army_shooting_capability import calculate_army_shooting_output_density
from courage_integration_contract import build_courage_integration_contract
from i2i_c3_b8a_cohort_intake import FIXTURES, FIXTURE_DIR
from i2i_c3_b8b_mechanical_qualification import load_reference_army_with_platforms
from i2i_c3_b8c_reference_qualification import read_json

ROOT = Path(__file__).resolve().parent
METRICS = ('offence', 'defence', 'mobility', 'shooting', 'courage')


def benchmark_target():
    b = DEFAULT_COMBAT_BENCHMARK
    return ConfiguredProfile(profile=Profile(
        id='D1_BENCHMARK', name='D1 Benchmark', points=0,
        movement=6, fight=b.fight, shooting='4+', strength=b.strength,
        defence=b.defence, attacks=b.attacks, wounds=b.wounds,
        courage='4+', intelligence='4+', might=0, will=0, fate=0,
        max_in_army=0,
    ))


def measure(value, units, assumption):
    val = float(value)
    if not math.isfinite(val):
        raise ValueError('Non-finite diagnostic measurement')
    return {'value': val, 'units': units, 'assumption': assumption, 'approved': False}


def extract(army, target):
    b = DEFAULT_COMBAT_BENCHMARK
    operations = {
        'offence': lambda: measure(
            calculate_army_offensive_output_density(army, b),
            'offensive_output_per_100_points', 'default F4 S4 D6 A1 opponent'),
        'defence': lambda: measure(
            calculate_mechanical_defence_diagnostics(army, b, engagements=3)['combat_density'],
            'survival_density_per_100_points', 'three engagements; no resurrection'),
        'mobility': lambda: measure(
            build_mobility_integration_contract(army).open_ground.value,
            'movement_accessibility_index', 'open ground; base-size penalty retained'),
        'shooting': lambda: measure(
            calculate_army_shooting_output_density(army=army, defender=target),
            'expected_wounds_per_100_points', 'stationary vs D6 benchmark'),
        'courage': lambda: measure(
            build_courage_integration_contract(army, target).friendly_reliability.value,
            'individual_test_pass_probability', 'standard test; no positional support'),
    }
    values, errors = {}, {}
    for key, calc in operations.items():
        try:
            values[key] = calc()
        except Exception as exc:
            values[key] = None
            errors[key] = f'{type(exc).__name__}: {exc}'
    return values, errors


def build_report(qualification, importer=load_reference_army_with_platforms):
    eligible = {r['army']: r for r in qualification.get('armies', [])
                if r.get('candidate_status') == 'provisional_reference'}
    gate = (qualification.get('stage') == 'B8-C' and
            qualification.get('status') == 'provisional_evidence_qualified' and
            qualification.get('provisional_references') == 6 and
            qualification.get('numerical_calibration_permitted') is False and
            set(eligible) == set(FIXTURES))
    if not gate:
        return {'stage': 'I2-I-D1', 'status': 'blocked_by_reference_gate',
                'rows': [], 'numerical_calibration_permitted': False,
                'production_scoring_modified': False}
    target = benchmark_target()
    rows = []
    for key, (filename, alignment, archetype) in FIXTURES.items():
        try:
            army = importer(FIXTURE_DIR / filename)
            values, issues = extract(army, target)
        except Exception as exc:
            values = {name: None for name in METRICS}
            issues = {'import': f'{type(exc).__name__}: {exc}'}
        rows.append({'army': key, 'alignment': alignment,
                     'proposed_archetype': archetype, 'points': eligible[key]['points'],
                     'measurements': values, 'issues': issues})
    complete = all(not row['issues'] and all(row['measurements'][m] is not None
                   for m in METRICS) for row in rows)
    return {'stage': 'I2-I-D1',
            'status': 'matrix_complete' if complete else 'matrix_incomplete',
            'rows': rows, 'metrics': METRICS,
            'other_five_metrics': 'excluded_not_zero',
            'calibration_thresholds_fitted': False,
            'numerical_calibration_permitted': False,
            'calibration_anchors_approved': False,
            'production_scoring_modified': False,
            'limitations': [
                'Different units: do not directly average the five numbers.',
                'Provisional benchmarks are not approved calibration anchors.',
                'Special-rule completeness and chariot behaviour remain unapproved.',
            ]}


if __name__ == '__main__':
    path = ROOT / 'b8c_reference_qualification.json'
    if not path.exists():
        print(json.dumps({'stage': 'I2-I-D1', 'status': 'missing_b8c_evidence'}, indent=2))
        raise SystemExit(2)
    print(json.dumps(build_report(read_json(path)), indent=2))
