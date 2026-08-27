import pytest

from scenario_demand import (
    ScenarioDemand,
    StrategicDemand,
    get_scenario_demand_intensity,
    get_scenario_demand_profile,
)



def test_strategic_demand_contains_all_initial_dimensions():
    assert (
        StrategicDemand.DISTRIBUTED_CONTROL.value
        == "distributed_control"
    )
    assert (
        StrategicDemand.CONCENTRATED_CONTROL.value
        == "concentrated_control"
    )
    assert (
        StrategicDemand.MOBILITY.value
        == "mobility"
    )
    assert (
        StrategicDemand.PROJECTION.value
        == "projection"
    )
    assert (
        StrategicDemand.OBJECT_INTERACTION.value
        == "object_interaction"
    )
    assert (
        StrategicDemand.ATTRITION_OUTPUT.value
        == "attrition_output"
    )
    assert (
        StrategicDemand.KEY_MODEL_PRESSURE.value
        == "key_model_pressure"
    )
    assert (
        StrategicDemand.KEY_MODEL_PRESERVATION.value
        == "key_model_preservation"
    )
    assert (
        StrategicDemand.STATE_RESILIENCE.value
        == "state_resilience"
    )
    assert (
        StrategicDemand.DEPLOYMENT_RECOVERY.value
        == "deployment_recovery"
    )


def test_scenario_demand_stores_dimension_and_intensity():
    demand = ScenarioDemand(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        intensity=0.8,
    )

    assert (
        demand.dimension
        is StrategicDemand.DISTRIBUTED_CONTROL
    )
    assert demand.intensity == 0.8


def test_scenario_demand_is_immutable():
    demand = ScenarioDemand(
        dimension=StrategicDemand.MOBILITY,
        intensity=0.5,
    )

    with pytest.raises(AttributeError):
        demand.intensity = 0.7


def test_scenario_demand_allows_zero_intensity():
    demand = ScenarioDemand(
        dimension=StrategicDemand.MOBILITY,
        intensity=0.0,
    )

    assert demand.intensity == 0.0


def test_scenario_demand_allows_full_intensity():
    demand = ScenarioDemand(
        dimension=StrategicDemand.MOBILITY,
        intensity=1.0,
    )

    assert demand.intensity == 1.0


def test_scenario_demand_rejects_negative_intensity():
    with pytest.raises(
        ValueError,
        match="Scenario demand intensity must be between 0.0 and 1.0.",
    ):
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=-0.01,
        )


def test_scenario_demand_rejects_intensity_above_one():
    with pytest.raises(
        ValueError,
        match="Scenario demand intensity must be between 0.0 and 1.0.",
    ):
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=1.01,
        )


def test_scenario_demand_rejects_invalid_dimension_type():
    with pytest.raises(
        TypeError,
        match="dimension must be a StrategicDemand.",
    ):
        ScenarioDemand(
            dimension="mobility",
            intensity=0.5,
        )

def test_get_scenario_demand_intensity_returns_matching_intensity():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            intensity=0.8,
        ),
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=0.5,
        ),
    )

    assert (
        get_scenario_demand_intensity(
            demands,
            StrategicDemand.MOBILITY,
        )
        == 0.5
    )


def test_get_scenario_demand_intensity_returns_zero_when_absent():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            intensity=0.8,
        ),
    )

    assert (
        get_scenario_demand_intensity(
            demands,
            StrategicDemand.MOBILITY,
        )
        == 0.0
    )


def test_get_scenario_demand_intensity_returns_zero_for_empty_profile():
    assert (
        get_scenario_demand_intensity(
            (),
            StrategicDemand.MOBILITY,
        )
        == 0.0
    )


def test_get_scenario_demand_intensity_rejects_invalid_dimension():
    with pytest.raises(
        TypeError,
        match="dimension must be a StrategicDemand.",
    ):
        get_scenario_demand_intensity(
            (),
            "mobility",
        )


def test_get_scenario_demand_intensity_rejects_invalid_demand_entries():
    with pytest.raises(
        TypeError,
        match="demands must contain only ScenarioDemand values.",
    ):
        get_scenario_demand_intensity(
            ("mobility",),
            StrategicDemand.MOBILITY,
        )

def test_get_scenario_demand_profile_returns_all_dimensions():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            intensity=0.8,
        ),
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=0.5,
        ),
    )

    profile = get_scenario_demand_profile(demands)

    assert profile == {
        StrategicDemand.DISTRIBUTED_CONTROL: 0.8,
        StrategicDemand.CONCENTRATED_CONTROL: 0.0,
        StrategicDemand.MOBILITY: 0.5,
        StrategicDemand.PROJECTION: 0.0,
        StrategicDemand.OBJECT_INTERACTION: 0.0,
        StrategicDemand.ATTRITION_OUTPUT: 0.0,
        StrategicDemand.KEY_MODEL_PRESSURE: 0.0,
        StrategicDemand.KEY_MODEL_PRESERVATION: 0.0,
        StrategicDemand.STATE_RESILIENCE: 0.0,
        StrategicDemand.DEPLOYMENT_RECOVERY: 0.0,
    }


def test_get_scenario_demand_profile_returns_all_zero_for_empty_profile():
    profile = get_scenario_demand_profile(())

    assert profile == {
        dimension: 0.0
        for dimension in StrategicDemand
    }


def test_get_scenario_demand_profile_rejects_invalid_entries():
    with pytest.raises(
        TypeError,
        match="demands must contain only ScenarioDemand values.",
    ):
        get_scenario_demand_profile(
            ("mobility",),
        )


def test_get_scenario_demand_profile_rejects_duplicate_dimensions():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=0.5,
        ),
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=0.8,
        ),
    )

    with pytest.raises(
        ValueError,
        match="demands cannot contain duplicate strategic dimensions.",
    ):
        get_scenario_demand_profile(demands)