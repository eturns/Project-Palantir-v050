import pytest

import balanced_objective

from army import Army
from balanced_objective import BalancedObjective
from balanced_objective_preset import (
    BALANCED_OBJECTIVE_PRESET,
)
from objective_score import (
    ObjectiveContribution,
    ObjectiveScore,
)
from optimiser_candidate import OptimiserCandidate


class FakeObjective:
    def __init__(
        self,
        score,
    ):
        self.score = score

    def evaluate(
        self,
        candidate,
    ):
        return self.score


def test_balanced_objective_score_returns_total_and_named_contributions(
    monkeypatch,
):
    candidate = OptimiserCandidate(
        army=Army(),
    )

    monkeypatch.setattr(
        balanced_objective,
        "build_balanced_objectives",
        lambda **kwargs: {
            "board_presence": FakeObjective(0.70),
            "battlefield_effects": FakeObjective(0.60),
            "combat_capability": FakeObjective(0.80),
            "magic": FakeObjective(0.40),
            "resource_endurance": FakeObjective(0.50),
        },
    )

    objective = BalancedObjective(
        preset=BALANCED_OBJECTIVE_PRESET,
        army_list="ARMY_LIST",
        combat_benchmark="BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    result = objective.score(
        candidate,
    )

    assert isinstance(
        result,
        ObjectiveScore,
    )

    assert result.total == pytest.approx(
        0.75 * 0.60
        + 0.25 * 0.40
    )

    assert result.contributions == (
        ObjectiveContribution(
            name="board_presence",
            value=0.70,
        ),
        ObjectiveContribution(
            name="battlefield_effects",
            value=0.60,
        ),
        ObjectiveContribution(
            name="combat_capability",
            value=0.80,
        ),
        ObjectiveContribution(
            name="magic",
            value=0.40,
        ),
        ObjectiveContribution(
            name="resource_endurance",
            value=0.50,
        ),
    )


def test_balanced_objective_evaluate_matches_transparent_score_total(
    monkeypatch,
):
    candidate = OptimiserCandidate(
        army=Army(),
    )

    monkeypatch.setattr(
        balanced_objective,
        "build_balanced_objectives",
        lambda **kwargs: {
            "board_presence": FakeObjective(0.60),
            "battlefield_effects": FakeObjective(0.60),
            "combat_capability": FakeObjective(0.60),
            "magic": FakeObjective(0.60),
            "resource_endurance": FakeObjective(0.60),
        },
    )

    objective = BalancedObjective(
        preset=BALANCED_OBJECTIVE_PRESET,
        army_list="ARMY_LIST",
        combat_benchmark="BENCHMARK",
        resource_assumption="RESOURCE_ASSUMPTION",
    )

    assert objective.evaluate(
        candidate,
    ) == objective.score(
        candidate,
    ).total