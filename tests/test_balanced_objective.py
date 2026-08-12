import pytest

import balanced_objective

from army import Army
from balanced_objective_preset import (
    BALANCED_OBJECTIVE_PRESET,
)
from optimiser_candidate import OptimiserCandidate


class FakeObjective:
    def __init__(self, score):
        self.score = score

    def evaluate(self, candidate):
        return self.score


def test_balanced_objective_uses_weighted_overall_and_weakest_component(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    monkeypatch.setattr(
        balanced_objective,
        "build_balanced_objectives",
        lambda **kwargs: {
            "board_presence": FakeObjective(0.8),
            "battlefield_effects": FakeObjective(0.8),
            "combat_capability": FakeObjective(0.2),
            "magic": FakeObjective(0.2),
            "resource_endurance": FakeObjective(0.5),
        },
    )

    objective = balanced_objective.BalancedObjective(
        preset=BALANCED_OBJECTIVE_PRESET,
        army_list="ARMY_LIST",
        combat_benchmark="BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    score = objective.evaluate(
        candidate,
    )

    # Equal-weight overall capability:
    # (0.8 + 0.8 + 0.2 + 0.2 + 0.5) / 5 = 0.5
    #
    # Weakest capability = 0.2
    #
    # Balanced:
    # 0.75 * 0.5 + 0.25 * 0.2 = 0.425
    assert score == pytest.approx(0.425)


def test_balanced_objective_preserves_uniform_capability(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    monkeypatch.setattr(
        balanced_objective,
        "build_balanced_objectives",
        lambda **kwargs: {
            "board_presence": FakeObjective(0.6),
            "battlefield_effects": FakeObjective(0.6),
            "combat_capability": FakeObjective(0.6),
            "magic": FakeObjective(0.6),
            "resource_endurance": FakeObjective(0.6),
        },
    )

    objective = balanced_objective.BalancedObjective(
        preset=BALANCED_OBJECTIVE_PRESET,
        army_list="ARMY_LIST",
        combat_benchmark="BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(0.6)