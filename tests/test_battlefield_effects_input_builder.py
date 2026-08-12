import pytest

import battlefield_effects_input_builder

from army import Army
from army_list import ArmyList
from army_metrics_entity import ArmyMetrics
from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)
from faction import Faction


def test_build_battlefield_effects_inputs_normalises_metric_densities(
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

    monkeypatch.setattr(
        battlefield_effects_input_builder,
        "calculate_army_metric_densities",
        lambda army, army_list: ArmyMetrics(
            offence=3.25,
            defence=2.25,
            shooting=2.50,
            courage=3.25,
            command=2.50,
            hero_hunting=2.50,
        ),
    )

    inputs = (
        battlefield_effects_input_builder
        .build_battlefield_effects_inputs(
            army,
            army_list,
        )
    )

    assert isinstance(
        inputs,
        BattlefieldEffectsInputs,
    )

    assert inputs.offence == pytest.approx(0.8)
    assert inputs.defence == pytest.approx(0.8)
    assert inputs.shooting == pytest.approx(0.8)
    assert inputs.courage == pytest.approx(0.8)
    assert inputs.command == pytest.approx(0.8)
    assert inputs.hero_hunting == pytest.approx(0.8)