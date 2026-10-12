"""Pure sensitivity calculations; does not touch production scoring."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools/i2d_d1_mobility_sensitivity.py"
spec = importlib.util.spec_from_file_location("i2d_d1_mobility_sensitivity", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_terrain_endpoints_are_exact():
    assert module.blend_manoeuvrability(8, 4, 0) == 8
    assert module.blend_manoeuvrability(8, 4, 1) == 4


def test_terrain_blend_is_monotone_when_terrain_slows():
    values = [module.blend_manoeuvrability(8, 4, s) for s in module.TERRAIN_SHARES]
    assert values == sorted(values, reverse=True)


def test_no_terrain_penalty_is_invariant_to_terrain_share():
    assert {module.blend_manoeuvrability(6, 6, s) for s in module.TERRAIN_SHARES} == {6}


def test_approaches_have_distinct_benchmark_interpretations():
    assert module.reference_ratio(8, 8) == 1.0
    assert module.saturating_ratio(8, 8) == 0.5


def test_linear_saturates_but_scenario_style_does_not():
    assert module.reference_ratio(20, 8) == 1
    assert module.saturating_ratio(20, 8) < 1


def test_invalid_assumptions_are_rejected():
    with pytest.raises(ValueError):
        module.blend_manoeuvrability(6, 3, 1.2)
    with pytest.raises(ValueError):
        module.saturating_ratio(6, 0)


def test_fixture_result_count_and_provenance_are_preserved():
    sample = [{"army": "A", "source": "TEST_ONLY", "points": "100", "models": "10",
               "open_average": "6", "difficult_average": "3",
               "self_reposition_models": "1", "potential_anchor_pairs": "0"}]
    out = module.build_sensitivity(sample)
    assert len(out) == len(module.TERRAIN_SHARES) * len(module.BENCHMARKS)
    assert all(r["scoring_status"] == "SENSITIVITY_ONLY_NOT_PRODUCTION" for r in out)
    assert all(r["self_reposition_models_reported_only"] == 1 for r in out)
