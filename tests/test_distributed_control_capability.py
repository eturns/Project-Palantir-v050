import pytest
from loader import load_all_profiles
from relationship_loader import load_profile_special_rules
from rule_loader import load_special_rules
from distributed_control_capability import (
    calculate_distributed_control_capability,
    calculate_distributed_control_from_profiles,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_distributed_control_returns_capability():
    result = calculate_distributed_control_capability(
        scenario_presence=10,
        benchmark_presence=10,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        value=1.0,
    )


def test_distributed_control_scales_below_benchmark():
    result = calculate_distributed_control_capability(
        scenario_presence=5,
        benchmark_presence=10,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        value=0.5,
    )


def test_distributed_control_caps_above_benchmark():
    result = calculate_distributed_control_capability(
        scenario_presence=15,
        benchmark_presence=10,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        value=1.0,
    )


def test_distributed_control_allows_zero_presence():
    result = calculate_distributed_control_capability(
        scenario_presence=0,
        benchmark_presence=10,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        value=0.0,
    )


def test_distributed_control_rejects_negative_presence():
    with pytest.raises(
        ValueError,
        match="scenario_presence cannot be negative.",
    ):
        calculate_distributed_control_capability(
            scenario_presence=-1,
            benchmark_presence=10,
        )


def test_distributed_control_requires_positive_benchmark():
    with pytest.raises(
        ValueError,
        match="benchmark_presence must be greater than zero.",
    ):
        calculate_distributed_control_capability(
            scenario_presence=5,
            benchmark_presence=0,
        )


def test_distributed_control_rejects_non_numeric_presence():
    with pytest.raises(
        TypeError,
        match="scenario_presence must be int or float.",
    ):
        calculate_distributed_control_capability(
            scenario_presence="5",
            benchmark_presence=10,
        )


def test_distributed_control_rejects_non_numeric_benchmark():
    with pytest.raises(
        TypeError,
        match="benchmark_presence must be int or float.",
    ):
        calculate_distributed_control_capability(
            scenario_presence=5,
            benchmark_presence="10",
        )


def test_distributed_control_rejects_boolean_presence():
    with pytest.raises(
        TypeError,
        match="scenario_presence must be int or float.",
    ):
        calculate_distributed_control_capability(
            scenario_presence=True,
            benchmark_presence=10,
        )

def _load_profiles_with_special_rules():
    profiles = load_all_profiles()

    profiles_by_id = {
        profile.id: profile
        for profile in profiles
    }

    special_rules = load_special_rules()

    load_profile_special_rules(
        profiles_by_id,
        special_rules,
    )

    return profiles_by_id


def test_distributed_control_from_real_dol_guldur_profiles_uses_dominant():
    profiles = _load_profiles_with_special_rules()

    army_profiles = (
        profiles["DG_NEC"],
        profiles["DG_WK"],
        profiles["DG_KHM"],
        profiles["DG_DH"],
        profiles["DG_FS"],
        profiles["DG_LS"],
        profiles["DG_AK"],
    )

    result = calculate_distributed_control_from_profiles(
        profiles=army_profiles,
        benchmark_presence=20,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        value=0.85,
    )


def test_distributed_control_from_profiles_caps_at_one():
    profiles = _load_profiles_with_special_rules()

    army_profiles = (
        profiles["DG_NEC"],
        profiles["DG_WK"],
        profiles["DG_KHM"],
        profiles["DG_DH"],
        profiles["DG_FS"],
        profiles["DG_LS"],
        profiles["DG_AK"],
    )

    result = calculate_distributed_control_from_profiles(
        profiles=army_profiles,
        benchmark_presence=10,
    )

    assert result == ScenarioCapability(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        value=1.0,
    )