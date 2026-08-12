import pytest

import battlefield_effects_objective

from army import Army
from army_list import ArmyList
from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)
from battlefield_effects_objective import (
    BattlefieldEffectsObjective,
)
from faction import Faction
from optimiser_candidate import OptimiserCandidate


def test_battlefield_effects_objective_evaluates_candidate(
    monkeypatch,
):
    army = Army()

    army_list = ArmyList(
        id="TEST_LIST",
        name="Test List",
        faction=Faction(
            id="TEST_FACTION",
            name="Test Faction",
        ),
    )

    candidate = OptimiserCandidate(
        army=army,
    )

    monkeypatch.setattr(
        battlefield_effects_objective,
        "build_battlefield_effects_inputs",
        lambda army, army_list: BattlefieldEffectsInputs(
            offence=0.9,
            defence=0.7,
            shooting=0.5,
            courage=0.3,
            command=0.1,
            hero_hunting=0.5,
        ),
    )

    objective = BattlefieldEffectsObjective(
        army_list=army_list,
    )

    score = objective.evaluate(
        candidate,
    )

    assert score == pytest.approx(0.5)