import pytest

from army import Army
from mobility_capability import (
    calculate_mobility_capability,
    calculate_mobility_capability_from_army,
)
from profiles import Profile
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def make_profile(
    *,
    profile_id: str,
    movement: int,
    base_size_mm: int = 25,
) -> Profile:
    return Profile(
        id=profile_id,
        name=profile_id,
        points=10,
        movement=movement,
        fight=3,
        shooting="4+",
        strength=3,
        defence=3,
        attacks=1,
        wounds=1,
        courage="4+",
        intelligence="4+",
        might=0,
        will=0,
        fate=0,
        max_in_army=1,
        base_size_mm=base_size_mm,
    )


def test_mobility_capability_matches_benchmark():
    result = calculate_mobility_capability(
        manoeuvrability=6.0,
        benchmark_manoeuvrability=6.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=1.0,
    )


def test_mobility_capability_scales_below_benchmark():
    result = calculate_mobility_capability(
        manoeuvrability=3.0,
        benchmark_manoeuvrability=6.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.5,
    )


def test_mobility_capability_caps_above_benchmark():
    result = calculate_mobility_capability(
        manoeuvrability=9.0,
        benchmark_manoeuvrability=6.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=1.0,
    )


def test_mobility_capability_allows_zero():
    result = calculate_mobility_capability(
        manoeuvrability=0.0,
        benchmark_manoeuvrability=6.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.0,
    )


def test_mobility_capability_rejects_negative_manoeuvrability():
    with pytest.raises(
        ValueError,
        match="manoeuvrability cannot be negative.",
    ):
        calculate_mobility_capability(
            manoeuvrability=-1.0,
            benchmark_manoeuvrability=6.0,
        )


def test_mobility_capability_requires_positive_benchmark():
    with pytest.raises(
        ValueError,
        match="benchmark_manoeuvrability must be greater than zero.",
    ):
        calculate_mobility_capability(
            manoeuvrability=6.0,
            benchmark_manoeuvrability=0.0,
        )


def test_mobility_capability_from_army_uses_existing_army_manoeuvrability():
    army = Army()

    army.add_profile(
        make_profile(
            profile_id="STANDARD",
            movement=6,
        ),
        quantity=2,
    )

    result = calculate_mobility_capability_from_army(
        army=army,
        benchmark_manoeuvrability=12.0,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.5,
    )