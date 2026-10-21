"""DEV-077-GT-D2C: compare the actual desktop adapter with the horde screenshot.

No calibration is modified; no assertion uses legacy metric density values.
The visual snapshot is a validation reference, not calibration truth.
"""
from math import isfinite
from pathlib import Path
import pytest

from desktop_analysis_adapter import run_analysis
from provisional_desktop_view import ORDER, build_provisional_summary
from provisional_calibration import EVALUATED, NOT_EVALUATED

ROOT = Path(__file__).resolve().parents[1]
HORDE = ROOT / 'tests' / 'fixtures' / 'goblin_town_700_horde.json'
EVALUATED_KEYS = (
    'offence_density', 'stationary_shooting', 'open_ground_mobility',
    'courage_reliability', 'army_survival_density', 'per_model_resilience',
)
UNEVALUATED_KEYS = ('magic', 'hero_hunting', 'control', 'command', 'objective')


@pytest.fixture(scope='module')
def desktop():
    assert HORDE.exists(), f'Missing horde fixture: {HORDE}'
    output = run_analysis(str(HORDE))
    assert output is not None, 'Desktop analysis returned no result'
    return output


@pytest.fixture(scope='module')
def rows(desktop):
    panel = desktop['provisional_capabilities']
    return {row['metric_id']: row for row in panel['metrics']}


def test_horde_army_identity(desktop):
    assert desktop['total_points'] == 700
    assert desktop['model_count'] == 79


def test_exact_presentation_order(rows):
    assert tuple(rows) == ORDER
    assert len(rows) == 11  # Defence deliberately has two submetrics.


@pytest.mark.parametrize('key', EVALUATED_KEYS)
def test_screenshot_qualified_metrics_are_numeric(rows, key):
    row = rows[key]
    assert row['status'] == EVALUATED
    assert row['rating'] is not None and isfinite(row['rating'])
    assert 0 <= row['rating'] <= 1
    assert row['raw_value'] is not None and isfinite(row['raw_value'])


@pytest.mark.parametrize('key', UNEVALUATED_KEYS)
def test_screenshot_unqualified_metrics_are_not_zero(rows, key):
    row = rows[key]
    assert row['status'] == NOT_EVALUATED
    assert row['rating'] is None


def test_screenshot_display_reference_values(rows):
    # Rounded to 3 places on screenshot. Tolerance accounts for display rounding.
    expected = {
        'offence_density': .793,
        'stationary_shooting': .000,
        'open_ground_mobility': .677,
        'courage_reliability': .510,
        'army_survival_density': 1.000,
        'per_model_resilience': .460,
    }
    for key, rating in expected.items():
        assert rows[key]['rating'] == pytest.approx(rating, abs=.001), key


def test_screenshot_raw_measurements(rows):
    expected = {
        'offence_density': .985,
        'stationary_shooting': .000,
        'open_ground_mobility': 4.933,
        'courage_reliability': .429,
        'army_survival_density': 4.366,
        'per_model_resilience': .387,
    }
    for key, raw in expected.items():
        assert rows[key]['raw_value'] == pytest.approx(raw, abs=.0015), key


def test_display_only_flags(desktop):
    panel = desktop['provisional_capabilities']
    assert panel['display_only'] is True
    assert panel['production_scoring_changed'] is False
    assert panel['defence_independent_composite_weighting_allowed'] is False
    assert panel['title'] == 'PROVISIONAL — SIX-ARMY REFERENCE'


def test_scenario_scores_preserved_and_finite(desktop):
    scores = {s['name']: s['score'] for s in desktop['scenarios']}
    assert len(scores) >= 20
    assert all(isfinite(s) and 0 <= s <= 1 for s in scores.values())
    assert scores['Domination'] == pytest.approx(.888, abs=.001)
    assert scores['Clash by Moonlight'] == pytest.approx(.000, abs=.001)


def test_desktop_summary_retains_unavailable_language(desktop):
    summary = build_provisional_summary(desktop['provisional_capabilities'])
    assert 'Magic: Not evaluated' in summary
    assert 'Objective: Not evaluated' in summary
    assert 'scenario and optimiser results unchanged' in summary
