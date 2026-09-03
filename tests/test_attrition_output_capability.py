import pytest

from army import Army
from attrition_output_capability import (
    calculate_attrition_output_capability,
    calculate_attrition_output_capability_from_army,
)
from combat_benchmark import (
    CombatBenchmark,
)
from profiles import Profile
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def make_profile(
    *,
    profile_id: str,
    fight: int = 4,
    strength: int = 4,
    defence: int = 6,
    attacks: int = 1,
    wounds: int = 1,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
        movement=6,
        fight=fight,
        shooting="4+",
        strength=strength,
        defence=defence,
        attacks=attacks,
        wounds=wounds,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
    )


def test_attrition_output_matches_benchmark_score():
    result = calculate_attrition_output_capability(
        combat_capability=1.0,
        benchmark_combat_capability=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.ATTRITION_OUTPUT,
        value=0.5,
    )


def test_attrition_output_scales_below_benchmark():
    result = calculate_attrition_output_capability(
        combat_capability=0.5,
        benchmark_combat_capability=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.ATTRITION_OUTPUT,
        value=0.5 / 1.5,
    )


def test_attrition_output_preserves_above_benchmark_difference():
    result = calculate_attrition_output_capability(
        combat_capability=1.5,
        benchmark_combat_capability=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.ATTRITION_OUTPUT,
        value=1.5 / 2.5,
    )


def test_attrition_output_allows_zero():
    result = calculate_attrition_output_capability(
        combat_capability=0.0,
        benchmark_combat_capability=1.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.ATTRITION_OUTPUT,
        value=0.0,
    )


def test_attrition_output_rejects_negative_combat_capability():
    with pytest.raises(
        ValueError,
        match="combat_capability cannot be negative.",
    ):
        calculate_attrition_output_capability(
            combat_capability=-0.1,
            benchmark_combat_capability=1.0,
        )


def test_attrition_output_requires_positive_benchmark():
    with pytest.raises(
        ValueError,
        match="benchmark_combat_capability must be greater than zero.",
    ):
        calculate_attrition_output_capability(
            combat_capability=1.0,
            benchmark_combat_capability=0.0,
        )


def test_attrition_output_from_army_uses_existing_combat_capability():
    army = Army()

    army.add_profile(
        make_profile(
            profile_id="BENCHMARK",
        ),
    )

    benchmark = CombatBenchmark(
        fight=4,
        strength=4,
        defence=6,
        attacks=1,
        wounds=1,
    )

    result = calculate_attrition_output_capability_from_army(
        army=army,
        combat_benchmark=benchmark,
        benchmark_combat_capability=0.5,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.ATTRITION_OUTPUT,
        value=0.5,
    )