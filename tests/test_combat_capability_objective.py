import pytest

import combat_capability_objective

from army import Army
from combat_capability_objective import (
    CombatCapabilityObjective,
)
from optimiser_candidate import OptimiserCandidate


from combat_benchmark import (
    CombatBenchmark,
    DEFAULT_COMBAT_BENCHMARK,
)
from combat_benchmark_portfolio import (
    CombatBenchmarkPortfolio,
    WeightedCombatBenchmark,
)

def test_combat_capability_objective_evaluates_candidate(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    monkeypatch.setattr(
        combat_capability_objective,
        "calculate_army_combat_capability",
        lambda army, benchmark: 0.64,
    )

    objective = CombatCapabilityObjective(
        benchmark=DEFAULT_COMBAT_BENCHMARK,
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(0.64)

def test_combat_capability_objective_evaluates_weighted_portfolio(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    warrior = CombatBenchmark(
        fight=4,
        strength=3,
        defence=5,
        attacks=1,
        wounds=1,
    )

    hero = CombatBenchmark(
        fight=6,
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
    )

    portfolio = CombatBenchmarkPortfolio(
        name="Test Portfolio",
        benchmarks=(
            WeightedCombatBenchmark(
                name="Warrior",
                benchmark=warrior,
                weight=0.60,
            ),
            WeightedCombatBenchmark(
                name="Hero",
                benchmark=hero,
                weight=0.40,
            ),
        ),
    )

    scores = {
        warrior: 0.80,
        hero: 0.50,
    }

    monkeypatch.setattr(
        combat_capability_objective,
        "calculate_army_combat_capability",
        lambda army, benchmark: scores[benchmark],
    )

    objective = CombatCapabilityObjective(
        benchmark=portfolio,
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(
        (0.80 * 0.60)
        + (0.50 * 0.40)
    )