import pytest
from army import Army
from faction import Faction
from army_list import ArmyList
from combat_benchmark import CombatBenchmark
from battlefield_effects_inputs import BattlefieldEffectsInputs
from key_model_pressure_capability import (
    calculate_key_model_pressure_capability,
    calculate_key_model_pressure_from_army,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_key_model_pressure_is_equal_weight_average():
    result = calculate_key_model_pressure_capability(
        attrition_output=0.8,
        hero_hunting=0.6,
    )

    assert (
        result.dimension
        == StrategicDemand.KEY_MODEL_PRESSURE
    )
    assert result.value == pytest.approx(0.7)


def test_key_model_pressure_is_one_when_both_inputs_are_one():
    result = calculate_key_model_pressure_capability(
        attrition_output=1.0,
        hero_hunting=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESSURE,
        value=1.0,
    )


def test_key_model_pressure_is_zero_when_both_inputs_are_zero():
    result = calculate_key_model_pressure_capability(
        attrition_output=0.0,
        hero_hunting=0.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESSURE,
        value=0.0,
    )


@pytest.mark.parametrize(
    "attrition_output, hero_hunting",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_key_model_pressure_rejects_values_outside_zero_to_one(
    attrition_output,
    hero_hunting,
):
    with pytest.raises(
        ValueError,
        match="capability inputs must be between 0.0 and 1.0.",
    ):
        calculate_key_model_pressure_capability(
            attrition_output=attrition_output,
            hero_hunting=hero_hunting,
        )


@pytest.mark.parametrize(
    "attrition_output, hero_hunting",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (True, 0.5),
        (0.5, False),
    ],
)
def test_key_model_pressure_rejects_non_numeric_inputs(
    attrition_output,
    hero_hunting,
):
    with pytest.raises(
        TypeError,
        match="capability inputs must be int or float.",
    ):
        calculate_key_model_pressure_capability(
            attrition_output=attrition_output,
            hero_hunting=hero_hunting,
        )

def test_key_model_pressure_from_army_combines_attrition_and_hero_hunting(
    monkeypatch,
):
    import key_model_pressure_capability

    army = Army()

    faction = Faction(
        id="TEST_FACTION",
        name="Test Faction",
    )

    army_list = ArmyList(
        id="TEST",
        name="Test",
        faction=faction,
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        key_model_pressure_capability,
        "calculate_attrition_output_capability_from_army",
        lambda army, combat_benchmark, benchmark_combat_capability: (
            ScenarioCapability(
                dimension=StrategicDemand.ATTRITION_OUTPUT,
                value=0.8,
            )
        ),
    )

    monkeypatch.setattr(
        key_model_pressure_capability,
        "build_battlefield_effects_inputs",
        lambda army, army_list: BattlefieldEffectsInputs(
            offence=0.0,
            defence=0.0,
            shooting=0.0,
            courage=0.0,
            command=0.0,
            hero_hunting=0.6,
        ),
    )

    result = calculate_key_model_pressure_from_army(
        army=army,
        army_list=army_list,
        combat_benchmark=benchmark,
        benchmark_combat_capability=0.5,
    )

    assert (
        result.dimension
        == StrategicDemand.KEY_MODEL_PRESSURE
    )
    assert result.value == pytest.approx(0.7)