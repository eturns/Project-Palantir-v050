from combat_benchmark import (
    CombatBenchmark,
    DEFAULT_COMBAT_BENCHMARK,
)


def test_combat_benchmark_stores_explicit_combat_assumptions():
    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    assert benchmark.fight == 4
    assert benchmark.strength == 4
    assert benchmark.defence == 6
    assert benchmark.attacks == 1
    assert benchmark.wounds == 1

def test_default_combat_benchmark_is_explicit_v1_assumption():
    assert DEFAULT_COMBAT_BENCHMARK == CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )