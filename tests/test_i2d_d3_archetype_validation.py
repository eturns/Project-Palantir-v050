"""DEV-077S-I2-D-D3 — archetype comparison contract tests."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/i2d_d3_archetype_validation.py'
spec = importlib.util.spec_from_file_location('i2d_d3_archetype_validation', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def metrics():
    return {k: module.aggregate_army_mobility(a) for k, a in module.archetype_armies().items()}


def test_all_archetypes_provide_all_exposure_scenarios():
    rows = module.diagnostic_rows()
    assert len(rows) == 6 * 5
    assert {r['terrain_share_assumption'] for r in rows} == set(module.TERRAIN_SHARES)
    assert all(r['score_status'] == 'DIAGNOSTIC_NOT_PRODUCTION' for r in rows)


def test_horde_gains_total_not_average_mobility():
    m = metrics()
    assert m['infantry_horde'].model_count > m['small_elite'].model_count
    assert m['infantry_horde'].total_open_ground > m['small_elite'].total_open_ground
    assert m['infantry_horde'].average_open_ground < m['small_elite'].average_open_ground


def test_terrain_specialists_retain_full_mobility():
    m = metrics()['terrain_specialists']
    assert m.terrain_retention == pytest.approx(1.0)
    assert m.average_difficult_terrain == pytest.approx(m.average_open_ground)


def test_terrain_specialists_overtake_nonexempt_fast_large_base():
    rows = module.diagnostic_rows()
    open_ranks = [r['archetype'] for r in module.rank_at(rows, 0)]
    difficult_ranks = [r['archetype'] for r in module.rank_at(rows, 1)]
    assert open_ranks.index('large_base_fast') < open_ranks.index('terrain_specialists')
    assert difficult_ranks.index('terrain_specialists') < difficult_ranks.index('large_base_fast')


def test_base_size_alters_efficiency_at_same_move():
    m = metrics()
    # Both comparable profiles have Move 8; large-base specialists are
    # terrain exempt so only compare OPEN-GROUND movement.
    assert m['same_speed_small_base'].average_open_ground > m['terrain_specialists'].average_open_ground


def test_no_row_is_called_a_standardised_score():
    assert all('normalised' not in row and 'rating' not in row for row in module.diagnostic_rows())


def test_points_efficiency_and_mean_can_disagree():
    m = metrics()
    assert m['infantry_horde'].open_ground_per_100_points > m['small_elite'].open_ground_per_100_points
    assert m['infantry_horde'].average_open_ground < m['small_elite'].average_open_ground
