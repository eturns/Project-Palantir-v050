import pytest
from combat_benchmark import CombatBenchmark
from profiles import Profile
from key_model_preservation_capability import (
    calculate_key_model_preservation_capability,
    calculate_key_model_preservation_from_profile,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_key_model_preservation_is_equal_weight_average():
    result = calculate_key_model_preservation_capability(
        defensive_survivability=0.8,
        protective_resources=0.6,
    )

    assert (
        result.dimension
        == StrategicDemand.KEY_MODEL_PRESERVATION
    )
    assert result.value == pytest.approx(0.7)


def test_key_model_preservation_is_one_when_both_inputs_are_one():
    result = calculate_key_model_preservation_capability(
        defensive_survivability=1.0,
        protective_resources=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
        value=1.0,
    )


def test_key_model_preservation_is_zero_when_both_inputs_are_zero():
    result = calculate_key_model_preservation_capability(
        defensive_survivability=0.0,
        protective_resources=0.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
        value=0.0,
    )


@pytest.mark.parametrize(
    "defensive_survivability, protective_resources",
    [
        (-0.1, 0.5),
        (1.1, 0.5),
        (0.5, -0.1),
        (0.5, 1.1),
    ],
)
def test_key_model_preservation_rejects_values_outside_zero_to_one(
    defensive_survivability,
    protective_resources,
):
    with pytest.raises(
        ValueError,
        match="capability inputs must be between 0.0 and 1.0.",
    ):
        calculate_key_model_preservation_capability(
            defensive_survivability=defensive_survivability,
            protective_resources=protective_resources,
        )


@pytest.mark.parametrize(
    "defensive_survivability, protective_resources",
    [
        ("0.5", 0.5),
        (0.5, "0.5"),
        (True, 0.5),
        (0.5, False),
    ],
)
def test_key_model_preservation_rejects_non_numeric_inputs(
    defensive_survivability,
    protective_resources,
):
    with pytest.raises(
        TypeError,
        match="capability inputs must be int or float.",
    ):
        calculate_key_model_preservation_capability(
            defensive_survivability=defensive_survivability,
            protective_resources=protective_resources,
        )

def test_key_model_preservation_from_profile_combines_staying_power_and_fate(
    monkeypatch,
):
    import key_model_preservation_capability

    profile = Profile(
        id="KEY",
        name="Key Model",
        points=100,
        movement=6,
        fight=5,
        shooting="4+",
        strength=4,
        defence=6,
        attacks=2,
        wounds=2,
        courage="4+",
        intelligence="4+",
        might=2,
        will=2,
        fate=2,
        max_in_army=1,
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    monkeypatch.setattr(
        key_model_preservation_capability,
        "calculate_staying_power_from_profile",
        lambda profile, benchmark: 0.8,
    )

    result = calculate_key_model_preservation_from_profile(
        profile=profile,
        benchmark=benchmark,
        benchmark_fate=4,
    )

    assert (
        result.dimension
        == StrategicDemand.KEY_MODEL_PRESERVATION
    )

    assert result.value == pytest.approx(
        (
            0.8
            + 0.5
        ) / 2
    )