import pytest

from scenario_capability import (
    ScenarioCapability,
    ScenarioCapabilityProfile,
)
from scenario_demand import StrategicDemand


def test_scenario_capability_stores_dimension_and_value():
    capability = ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.75,
    )

    assert capability.dimension is StrategicDemand.MOBILITY
    assert capability.value == 0.75


def test_scenario_capability_is_immutable():
    capability = ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.5,
    )

    with pytest.raises(AttributeError):
        capability.value = 0.8


def test_scenario_capability_allows_zero():
    capability = ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.0,
    )

    assert capability.value == 0.0


def test_scenario_capability_allows_one():
    capability = ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=1.0,
    )

    assert capability.value == 1.0


def test_scenario_capability_rejects_invalid_dimension():
    with pytest.raises(
        TypeError,
        match="dimension must be a StrategicDemand.",
    ):
        ScenarioCapability(
            dimension="mobility",
            value=0.5,
        )


def test_scenario_capability_rejects_negative_value():
    with pytest.raises(
        ValueError,
        match="Scenario capability value must be between 0.0 and 1.0.",
    ):
        ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value=-0.01,
        )


def test_scenario_capability_rejects_value_above_one():
    with pytest.raises(
        ValueError,
        match="Scenario capability value must be between 0.0 and 1.0.",
    ):
        ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value=1.01,
        )


def test_scenario_capability_rejects_non_numeric_value():
    with pytest.raises(
        TypeError,
        match="Scenario capability value must be int or float.",
    ):
        ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value="high",
        )


def test_scenario_capability_rejects_boolean_value():
    with pytest.raises(
        TypeError,
        match="Scenario capability value must be int or float.",
    ):
        ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value=True,
        )

def test_scenario_capability_profile_stores_capabilities():
    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.8,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.PROJECTION,
                value=0.6,
            ),
        ),
    )

    assert profile.capabilities == (
        ScenarioCapability(
            dimension=StrategicDemand.MOBILITY,
            value=0.8,
        ),
        ScenarioCapability(
            dimension=StrategicDemand.PROJECTION,
            value=0.6,
        ),
    )


def test_scenario_capability_profile_defaults_to_empty():
    profile = ScenarioCapabilityProfile()

    assert profile.capabilities == ()


def test_scenario_capability_profile_is_immutable():
    profile = ScenarioCapabilityProfile()

    with pytest.raises(AttributeError):
        profile.capabilities = ()


def test_scenario_capability_profile_rejects_invalid_entries():
    with pytest.raises(
        TypeError,
        match="capabilities must contain only ScenarioCapability values.",
    ):
        ScenarioCapabilityProfile(
            capabilities=("mobility",),
        )


def test_scenario_capability_profile_rejects_duplicate_dimensions():
    with pytest.raises(
        ValueError,
        match="Capability profile cannot contain duplicate strategic dimensions.",
    ):
        ScenarioCapabilityProfile(
            capabilities=(
                ScenarioCapability(
                    dimension=StrategicDemand.MOBILITY,
                    value=0.5,
                ),
                ScenarioCapability(
                    dimension=StrategicDemand.MOBILITY,
                    value=0.8,
                ),
            ),
        )


def test_scenario_capability_profile_returns_matching_value():
    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.75,
            ),
        ),
    )

    assert (
        profile.get_value(StrategicDemand.MOBILITY)
        == 0.75
    )


def test_scenario_capability_profile_returns_zero_when_dimension_absent():
    profile = ScenarioCapabilityProfile()

    assert (
        profile.get_value(StrategicDemand.MOBILITY)
        == 0.0
    )


def test_scenario_capability_profile_rejects_invalid_lookup_dimension():
    profile = ScenarioCapabilityProfile()

    with pytest.raises(
        TypeError,
        match="dimension must be a StrategicDemand.",
    ):
        profile.get_value("mobility")


def test_scenario_capability_profile_converts_to_complete_mapping():
    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.75,
            ),
        ),
    )

    mapping = profile.to_mapping()

    assert mapping == {
        dimension: (
            0.75
            if dimension is StrategicDemand.MOBILITY
            else 0.0
        )
        for dimension in StrategicDemand
    }

def test_capability_profile_reports_present_dimension_as_available():
    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.7,
            ),
        ),
    )

    assert profile.has_capability(
        StrategicDemand.MOBILITY,
    ) is True


def test_capability_profile_reports_absent_dimension_as_unavailable():
    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.7,
            ),
        ),
    )

    assert profile.has_capability(
        StrategicDemand.OBJECT_INTERACTION,
    ) is False


def test_get_capability_returns_present_capability():
    capability = ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.7,
    )

    profile = ScenarioCapabilityProfile(
        capabilities=(capability,),
    )

    assert profile.get_capability(
        StrategicDemand.MOBILITY,
    ) == capability


def test_get_capability_returns_none_when_dimension_is_unavailable():
    profile = ScenarioCapabilityProfile()

    assert profile.get_capability(
        StrategicDemand.OBJECT_INTERACTION,
    ) is None


def test_available_mapping_contains_only_available_capabilities():
    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.7,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.PROJECTION,
                value=0.4,
            ),
        ),
    )

    assert profile.to_available_mapping() == {
        StrategicDemand.MOBILITY: 0.7,
        StrategicDemand.PROJECTION: 0.4,
    }

    assert (
        StrategicDemand.OBJECT_INTERACTION
        not in profile.to_available_mapping()
    )