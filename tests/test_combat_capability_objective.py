import pytest

import combat_capability_objective

from army import Army
from combat_benchmark import DEFAULT_COMBAT_BENCHMARK
from combat_capability_objective import (
    CombatCapabilityObjective,
)
from optimiser_candidate import OptimiserCandidate


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