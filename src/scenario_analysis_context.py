from dataclasses import dataclass

from combat_benchmark import (
    DEFAULT_COMBAT_BENCHMARK,
    CombatBenchmark,
)


BASELINE_POINTS_LIMIT = 700.0
BASELINE_BENCHMARK_PRESENCE = 10.0

DEFAULT_BENCHMARK_MANOEUVRABILITY = 6.0
DEFAULT_BENCHMARK_COMBAT_CAPABILITY = 0.5
DEFAULT_BENCHMARK_FATE = 3.0


@dataclass(frozen=True)
class ScenarioAnalysisContext:
    combat_benchmark: CombatBenchmark
    benchmark_presence: float
    benchmark_manoeuvrability: float
    benchmark_combat_capability: float
    benchmark_fate: float


def calculate_benchmark_presence(
    *,
    points_limit: int | float,
) -> float:
    return (
        BASELINE_BENCHMARK_PRESENCE
        * points_limit
        / BASELINE_POINTS_LIMIT
    )


def build_default_scenario_analysis_context(
    *,
    points_limit: int | float,
) -> ScenarioAnalysisContext:
    return ScenarioAnalysisContext(
        combat_benchmark=DEFAULT_COMBAT_BENCHMARK,
        benchmark_presence=calculate_benchmark_presence(
            points_limit=points_limit,
        ),
        benchmark_manoeuvrability=(
            DEFAULT_BENCHMARK_MANOEUVRABILITY
        ),
        benchmark_combat_capability=(
            DEFAULT_BENCHMARK_COMBAT_CAPABILITY
        ),
        benchmark_fate=DEFAULT_BENCHMARK_FATE,
    )