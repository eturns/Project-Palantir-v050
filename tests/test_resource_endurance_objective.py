import pytest

import resource_endurance_objective

from army import Army
from battle_length_assumption import BattleHorizon
from optimiser_candidate import OptimiserCandidate
from resource_endurance_assumption import (
    ResourceEnduranceAssumption,
)
from resource_endurance_objective import (
    ResourceEnduranceObjective,
)
from resource_strategy import ResourceStrategy


def test_resource_endurance_objective_evaluates_candidate(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    assumption = ResourceEnduranceAssumption(
        horizon=BattleHorizon.MEDIUM,
        strategy=ResourceStrategy.BALANCED,
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_totals",
        lambda army: "RESOURCES",
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_trajectory",
        lambda resources, assumption: "TRAJECTORY",
    )

    monkeypatch.setattr(
        resource_endurance_objective,
        "calculate_army_resource_endurance",
        lambda resources, trajectory: 0.72,
    )

    objective = ResourceEnduranceObjective(
        assumption=assumption,
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(0.72)