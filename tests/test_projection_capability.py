import pytest

from battlefield_effects_inputs import (
    BattlefieldEffectsInputs,
)
from army import Army
from army_list import ArmyList
from faction import Faction

from projection_capability import (
    calculate_projection_capability,
    calculate_projection_capability_from_inputs,
    calculate_projection_capability_from_army,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_projection_capability_stores_score():
    result = calculate_projection_capability(
        battlefield_effects_score=0.75,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.PROJECTION,
        value=0.75,
    )


def test_projection_capability_allows_zero():
    result = calculate_projection_capability(
        battlefield_effects_score=0.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.PROJECTION,
        value=0.0,
    )


def test_projection_capability_allows_one():
    result = calculate_projection_capability(
        battlefield_effects_score=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.PROJECTION,
        value=1.0,
    )


def test_projection_capability_rejects_negative_score():
    with pytest.raises(
        ValueError,
        match="battlefield_effects_score must be between 0.0 and 1.0.",
    ):
        calculate_projection_capability(
            battlefield_effects_score=-0.01,
        )


def test_projection_capability_rejects_score_above_one():
    with pytest.raises(
        ValueError,
        match="battlefield_effects_score must be between 0.0 and 1.0.",
    ):
        calculate_projection_capability(
            battlefield_effects_score=1.01,
        )


def test_projection_capability_rejects_non_numeric_score():
    with pytest.raises(
        TypeError,
        match="battlefield_effects_score must be int or float.",
    ):
        calculate_projection_capability(
            battlefield_effects_score="0.5",
        )


def test_projection_capability_rejects_boolean_score():
    with pytest.raises(
        TypeError,
        match="battlefield_effects_score must be int or float.",
    ):
        calculate_projection_capability(
            battlefield_effects_score=True,
        )


def test_projection_capability_from_inputs_uses_existing_score():
    inputs = BattlefieldEffectsInputs(
        offence=0.5,
        defence=0.5,
        shooting=0.5,
        courage=0.5,
        command=0.5,
        hero_hunting=0.5,
    )

    result = calculate_projection_capability_from_inputs(
        inputs=inputs,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.PROJECTION,
        value=0.5,
    )

def test_projection_capability_from_army_uses_existing_builder(
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

    expected_inputs = BattlefieldEffectsInputs(
        offence=0.6,
        defence=0.6,
        shooting=0.6,
        courage=0.6,
        command=0.6,
        hero_hunting=0.6,
    )

    import projection_capability

    monkeypatch.setattr(
        projection_capability,
        "build_battlefield_effects_inputs",
        lambda army, army_list: expected_inputs,
    )

    result = calculate_projection_capability_from_army(
        army=army,
        army_list=army_list,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.PROJECTION,
        value=0.6,
    )