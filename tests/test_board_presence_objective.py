import pytest

import board_presence_objective

from army import Army
from army_list import ArmyList
from board_presence_inputs import BoardPresenceInputs
from faction import Faction
from optimiser_candidate import OptimiserCandidate


def test_board_presence_objective_scores_candidate(
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
        board_presence_objective,
        "build_board_presence_inputs",
        lambda army, army_list: BoardPresenceInputs(
            model_presence=0.5,
            manoeuvrability=0.6,
            control=0.7,
        ),
    )

    objective = (
        board_presence_objective
        .BoardPresenceObjective(
            army_list=army_list,
        )
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(
        0.58,
    )