import pytest
from army import Army
from combat_benchmark import CombatBenchmark
from profiles import Profile
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand
from state_resilience_capability import (
    calculate_state_resilience_capability,
    calculate_state_resilience_from_army,
)


def test_state_resilience_is_equal_weight_average():
    result = calculate_state_resilience_capability(
        model_state_capacity=0.8,
        resource_capacity=0.6,
    )

    assert (
        result.dimension
        == StrategicDemand.STATE_RESILIENCE
    )
    assert result.value == pytest.approx(0.7)


def test_state_resilience_is_one_when_both_inputs_are_one():
    result = calculate_state_resilience_capability(
        model_state_capacity=1.0,
        resource_capacity=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=1.0,
    )


def test_state_resilience_is_zero_when_both_inputs_are_zero():
    result = calculate_state_resilience_capability(
        model_state_capacity=0.0,
        resource_capacity=0.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.0,
    )


@pytest.mark.parametrize(
    "model_state_capacity, resource_capacity",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_state_resilience_rejects_values_outside_zero_to_one(
    model_state_capacity,
    resource_capacity,
):
    with pytest.raises(
        ValueError,
        match="capability inputs must be between 0.0 and 1.0.",
    ):
        calculate_state_resilience_capability(
            model_state_capacity=model_state_capacity,
            resource_capacity=resource_capacity,
        )


@pytest.mark.parametrize(
    "model_state_capacity, resource_capacity",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (True, 0.5),
        (0.5, False),
    ],
)
def test_state_resilience_rejects_non_numeric_inputs(
    model_state_capacity,
    resource_capacity,
):
    with pytest.raises(
        TypeError,
        match="capability inputs must be int or float.",
    ):
        calculate_state_resilience_capability(
            model_state_capacity=model_state_capacity,
            resource_capacity=resource_capacity,
        )

def test_state_resilience_from_army_combines_staying_power_and_resources(
    monkeypatch,
):
    import state_resilience_capability

    army = Army()

    profile = Profile(
        id="TEST",
        name="Test",
        points=100,
        movement=6,
        fight=4,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=1,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=1,
        max_in_army=1,
    )

    army.add_profile(
        profile,
        quantity=1,
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        state_resilience_capability,
        "calculate_army_staying_power",
        lambda army, benchmark: 0.8,
    )

    monkeypatch.setattr(
        state_resilience_capability,
        "calculate_resource_capacity_score",
        lambda might, will, fate, army_points: 0.6,
    )

    result = calculate_state_resilience_from_army(
        army=army,
        benchmark=benchmark,
    )

    assert result.dimension == StrategicDemand.STATE_RESILIENCE
    assert result.value == pytest.approx(0.7)