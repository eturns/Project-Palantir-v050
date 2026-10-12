"""Focused pure-function tests for the standalone D2 sensitivity tool."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / 'tools/i2d_d2_battlefield_ranking.py'
spec = importlib.util.spec_from_file_location('i2d_d2_battlefield_ranking', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def row(name, opening, difficult):
    return {'army': name, 'source': 'TEST_SYNTHETIC', 'open_average': opening,
            'difficult_average': difficult}


def test_blend_endpoints():
    assert module.blended(8, 4, 0) == 8
    assert module.blended(8, 4, 1) == 4


def test_blend_straight_line():
    assert module.blended(8, 4, .25) == 7


def test_exact_crossover_detected():
    assert module.crossover(row('A', 8, 2), row('B', 6, 6)) == pytest.approx(1/3)


def test_no_crossover_for_constant_ranking():
    assert module.crossover(row('A', 8, 6), row('B', 5, 4)) is None


def test_parallel_lines_no_unique_crossover():
    assert module.crossover(row('A', 8, 4), row('B', 7, 3)) is None


def test_rank_flips_at_crossover():
    ranks, _ = module.evaluate([row('A', 8, 2), row('B', 6, 6)])
    def leader(share):
        return next(r['army'] for r in ranks if r['terrain_share']==share
                    and r['benchmark']==8 and r['rank']==1)
    assert leader(0) == 'A'
    assert leader(1) == 'B'


def test_monotone_normalisation_preserves_raw_order_without_saturation():
    ranks, _ = module.evaluate([row('A', 8, 4), row('B', 5, 3)])
    snap = [r for r in ranks if r['terrain_share']==.5 and r['benchmark']==10]
    assert snap[0]['unnormalised_average'] > snap[1]['unnormalised_average']
    assert snap[0]['linear_reference'] > snap[1]['linear_reference']
    assert snap[0]['scenario_style'] > snap[1]['scenario_style']


def test_linear_saturation_can_hide_difference():
    ranks, _ = module.evaluate([row('A', 12, 12), row('B', 11, 11)])
    snap = [r for r in ranks if r['terrain_share']==.5 and r['benchmark']==8]
    assert snap[0]['linear_reference'] == snap[1]['linear_reference'] == 1
    assert snap[0]['scenario_style'] > snap[1]['scenario_style']


def test_invalid_and_duplicate_inputs_rejected():
    with pytest.raises(ValueError):
        module.blended(8, 4, 1.1)
    with pytest.raises(ValueError):
        module.blended(float('nan'), 4, .5)
    with pytest.raises(ValueError):
        module.evaluate([row('A', 4, 3), row('A', 6, 2)])


def test_grid_has_expected_row_counts_and_marks_assumptions():
    ranks, crossings = module.evaluate([row('A', 8, 4), row('B', 7, 5), row('C', 6, 3)])
    assert len(ranks) == 21 * 3 * 3
    assert len(crossings) == 3
    assert all(r['note'] == 'NOT_PRODUCTION__REPOSITION_EXCLUDED' for r in ranks)
