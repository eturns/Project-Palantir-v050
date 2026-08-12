import pytest

import magic_objective

from army import Army
from army_list import ArmyList
from army_metrics_entity import ArmyMetrics
from faction import Faction
from optimiser_candidate import OptimiserCandidate


def test_magic_objective_scores_candidate(
    monkeypatch,
):
    army = Army()

    candidate = OptimiserCandidate(
        army=army,
    )

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )

    monkeypatch.setattr(
        magic_objective,
        "calculate_army_metric_densities",
        lambda army, army_list: ArmyMetrics(
            magic=1.5,
        ),
    )

    objective = magic_objective.MagicObjective(
        army_list=army_list,
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(
        0.5,
    )