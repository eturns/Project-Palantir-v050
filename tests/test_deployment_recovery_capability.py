import pytest
from army import Army
from combat_benchmark import CombatBenchmark
from deployment_recovery_capability import (
    calculate_deployment_recovery_capability,
    calculate_deployment_recovery_from_army,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_deployment_recovery_is_equal_weight_average():
    result = calculate_deployment_recovery_capability(
        mobility=0.8,
        state_resilience=0.6,
    )

    assert (
        result.dimension
        == StrategicDemand.DEPLOYMENT_RECOVERY
    )
    assert result.value == pytest.approx(0.7)


def test_deployment_recovery_is_one_when_both_inputs_are_one():
    result = calculate_deployment_recovery_capability(
        mobility=1.0,
        state_resilience=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
        value=1.0,
    )


def test_deployment_recovery_is_zero_when_both_inputs_are_zero():
    result = calculate_deployment_recovery_capability(
        mobility=0.0,
        state_resilience=0.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DEPLOYMENT_RECOVERY,
        value=0.0,
    )


@pytest.mark.parametrize(
    "mobility, state_resilience",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_deployment_recovery_rejects_values_outside_zero_to_one(
    mobility,
    state_resilience,
):
    with pytest.raises(
        ValueError,
        match="capability inputs must be between 0.0 and 1.0.",
    ):
        calculate_deployment_recovery_capability(
            mobility=mobility,
            state_resilience=state_resilience,
        )


@pytest.mark.parametrize(
    "mobility, state_resilience",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (True, 0.5),
        (0.5, False),
    ],
)
def test_deployment_recovery_rejects_non_numeric_inputs(
    mobility,
    state_resilience,
):
    with pytest.raises(
        TypeError,
        match="capability inputs must be int or float.",
    ):
        calculate_deployment_recovery_capability(
            mobility=mobility,
            state_resilience=state_resilience,
        )

def test_deployment_recovery_from_army_combines_real_capabilities(
    monkeypatch,
):
    import deployment_recovery_capability

    army = Army()

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        deployment_recovery_capability,
        "calculate_mobility_capability_from_army",
        lambda army, benchmark_manoeuvrability: ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value=0.8,
        ),
    )

    monkeypatch.setattr(
        deployment_recovery_capability,
        "calculate_state_resilience_from_army",
        lambda army, benchmark: ScenarioCapability(
            dimension=StrategicDemand.STATE_RESILIENCE,
            value=0.6,
        ),
    )

    result = calculate_deployment_recovery_from_army(
        army=army,
        benchmark=benchmark,
        benchmark_manoeuvrability=1.0,
    )

    assert (
        result.dimension
        == StrategicDemand.DEPLOYMENT_RECOVERY
    )
    assert result.value == pytest.approx(0.7)