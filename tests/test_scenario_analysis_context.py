from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from scenario_analysis_context import (
    build_default_scenario_analysis_context,
    calculate_benchmark_presence,
)


def test_benchmark_presence_scales_from_700_point_calibration():
    assert calculate_benchmark_presence(
        points_limit=700,
    ) == 10.0

    assert calculate_benchmark_presence(
        points_limit=350,
    ) == 5.0

    assert calculate_benchmark_presence(
        points_limit=1400,
    ) == 20.0

def test_default_scenario_analysis_context_uses_canonical_defaults():
    context = build_default_scenario_analysis_context(
        points_limit=700,
    )

    assert (
        context.combat_benchmark
        is DEFAULT_COMBAT_BENCHMARK
    )

    assert context.benchmark_presence == 10.0
    assert context.benchmark_manoeuvrability == 6.0
    assert context.benchmark_combat_capability == 0.5
    assert context.benchmark_fate == 3.0

def test_default_scenario_analysis_context_scales_presence_only():
    context = build_default_scenario_analysis_context(
        points_limit=350,
    )

    assert context.benchmark_presence == 5.0

    assert context.benchmark_manoeuvrability == 6.0
    assert context.benchmark_combat_capability == 0.5
    assert context.benchmark_fate == 3.0