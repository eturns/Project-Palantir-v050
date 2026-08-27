import pytest
from army import Army
from combat_benchmark import CombatBenchmark
from concentrated_control_capability import (
    calculate_concentrated_control_capability,
    calculate_concentrated_control_from_army,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_concentrated_control_is_equal_weight_average():
    result = calculate_concentrated_control_capability(
        presence_strength=0.8,
        attrition_output=0.4,
    )

    assert (
        result.dimension
        == StrategicDemand.CONCENTRATED_CONTROL
    )
    assert result.value == pytest.approx(0.6)


def test_concentrated_control_is_one_when_both_inputs_are_one():
    result = calculate_concentrated_control_capability(
        presence_strength=1.0,
        attrition_output=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.CONCENTRATED_CONTROL,
        value=1.0,
    )


def test_concentrated_control_is_zero_when_both_inputs_are_zero():
    result = calculate_concentrated_control_capability(
        presence_strength=0.0,
        attrition_output=0.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.CONCENTRATED_CONTROL,
        value=0.0,
    )


@pytest.mark.parametrize(
    "presence_strength, attrition_output",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_concentrated_control_rejects_values_outside_zero_to_one(
    presence_strength,
    attrition_output,
):
    with pytest.raises(
        ValueError,
        match="capability inputs must be between 0.0 and 1.0.",
    ):
        calculate_concentrated_control_capability(
            presence_strength=presence_strength,
            attrition_output=attrition_output,
        )


@pytest.mark.parametrize(
    "presence_strength, attrition_output",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (True, 0.5),
        (0.5, False),
    ],
)
def test_concentrated_control_rejects_non_numeric_inputs(
    presence_strength,
    attrition_output,
):
    with pytest.raises(
        TypeError,
        match="capability inputs must be int or float.",
    ):
        calculate_concentrated_control_capability(
            presence_strength=presence_strength,
            attrition_output=attrition_output,
        )

def test_concentrated_control_from_army_combines_presence_and_attrition(
    monkeypatch,
):
    import concentrated_control_capability

    army = Army()

    combat_benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        concentrated_control_capability,
        "calculate_army_scenario_presence",
        lambda profiles: 8,
    )

    monkeypatch.setattr(
        concentrated_control_capability,
        "calculate_attrition_output_capability_from_army",
        lambda army, combat_benchmark, benchmark_combat_capability: (
            ScenarioCapability(
                dimension=StrategicDemand.ATTRITION_OUTPUT,
                value=0.4,
            )
        ),
    )

    result = calculate_concentrated_control_from_army(
        army=army,
        benchmark_presence=10,
        combat_benchmark=combat_benchmark,
        benchmark_combat_capability=0.5,
    )

    assert (
        result.dimension
        == StrategicDemand.CONCENTRATED_CONTROL
    )
    assert result.value == pytest.approx(0.6)