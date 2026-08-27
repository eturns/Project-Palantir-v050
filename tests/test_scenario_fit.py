import pytest

from scenario_demand import (
    ScenarioDemand,
    StrategicDemand,
)

from scenario_fit import (
    ScenarioFitResult,
    calculate_scenario_definition_fit,
    calculate_scenario_fit,
    calculate_scenario_fit_from_profile,
)

from scenario_definition import (
    DeploymentType,
    ScenarioDefinition,
    ScenarioPool,
    TerminationType,
)
from scenario_capability import (
    ScenarioCapability,
    ScenarioCapabilityProfile,
)
def test_scenario_fit_result_stores_score():
    result = ScenarioFitResult(
        score=0.75,
    )

    assert result.score == 0.75


def test_scenario_fit_result_is_immutable():
    result = ScenarioFitResult(
        score=0.5,
    )

    with pytest.raises(AttributeError):
        result.score = 0.8


def test_scenario_fit_result_allows_zero():
    result = ScenarioFitResult(
        score=0.0,
    )

    assert result.score == 0.0


def test_scenario_fit_result_allows_one():
    result = ScenarioFitResult(
        score=1.0,
    )

    assert result.score == 1.0


def test_scenario_fit_result_rejects_negative_score():
    with pytest.raises(
        ValueError,
        match="Scenario fit score must be between 0.0 and 1.0.",
    ):
        ScenarioFitResult(
            score=-0.01,
        )


def test_scenario_fit_result_rejects_score_above_one():
    with pytest.raises(
        ValueError,
        match="Scenario fit score must be between 0.0 and 1.0.",
    ):
        ScenarioFitResult(
            score=1.01,
        )

def test_scenario_fit_is_one_when_capabilities_fully_meet_demands():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=0.8,
        ),
        ScenarioDemand(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            intensity=0.6,
        ),
    )

    capabilities = {
        StrategicDemand.MOBILITY: 0.8,
        StrategicDemand.DISTRIBUTED_CONTROL: 0.6,
    }

    result = calculate_scenario_fit(
        demands=demands,
        capabilities=capabilities,
    )

    assert result == ScenarioFitResult(
        score=1.0,
    )


def test_scenario_fit_caps_credit_when_capability_exceeds_demand():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=0.5,
        ),
    )

    capabilities = {
        StrategicDemand.MOBILITY: 1.0,
    }

    result = calculate_scenario_fit(
        demands=demands,
        capabilities=capabilities,
    )

    assert result == ScenarioFitResult(
        score=1.0,
    )


def test_scenario_fit_is_zero_when_required_capability_is_zero():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=1.0,
        ),
    )

    capabilities = {
        StrategicDemand.MOBILITY: 0.0,
    }

    result = calculate_scenario_fit(
        demands=demands,
        capabilities=capabilities,
    )

    assert result == ScenarioFitResult(
        score=0.0,
    )


def test_scenario_fit_returns_partial_match():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=1.0,
        ),
    )

    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    result = calculate_scenario_fit(
        demands=demands,
        capabilities=capabilities,
    )

    assert result == ScenarioFitResult(
        score=0.4,
    )


def test_scenario_fit_weights_by_scenario_demand_intensity():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=1.0,
        ),
        ScenarioDemand(
            dimension=StrategicDemand.DISTRIBUTED_CONTROL,
            intensity=0.5,
        ),
    )

    capabilities = {
        StrategicDemand.MOBILITY: 0.5,
        StrategicDemand.DISTRIBUTED_CONTROL: 0.5,
    }

    result = calculate_scenario_fit(
        demands=demands,
        capabilities=capabilities,
    )

    assert result.score == pytest.approx(
        1.0 / 1.5,
    )


def test_scenario_fit_treats_missing_capability_as_zero():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=1.0,
        ),
    )

    result = calculate_scenario_fit(
        demands=demands,
        capabilities={},
    )

    assert result == ScenarioFitResult(
        score=0.0,
    )


def test_scenario_fit_returns_one_for_scenario_with_no_demands():
    result = calculate_scenario_fit(
        demands=(),
        capabilities={},
    )

    assert result == ScenarioFitResult(
        score=1.0,
    )

def test_scenario_fit_rejects_invalid_demand_entries():
    with pytest.raises(
        TypeError,
        match="demands must contain only ScenarioDemand values.",
    ):
        calculate_scenario_fit(
            demands=("mobility",),
            capabilities={},
        )


def test_scenario_fit_rejects_invalid_capability_dimension():
    with pytest.raises(
        TypeError,
        match="capabilities keys must be StrategicDemand values.",
    ):
        calculate_scenario_fit(
            demands=(),
            capabilities={
                "mobility": 0.5,
            },
        )


def test_scenario_fit_rejects_negative_capability():
    with pytest.raises(
        ValueError,
        match="Capability values must be between 0.0 and 1.0.",
    ):
        calculate_scenario_fit(
            demands=(),
            capabilities={
                StrategicDemand.MOBILITY: -0.01,
            },
        )


def test_scenario_fit_rejects_capability_above_one():
    with pytest.raises(
        ValueError,
        match="Capability values must be between 0.0 and 1.0.",
    ):
        calculate_scenario_fit(
            demands=(),
            capabilities={
                StrategicDemand.MOBILITY: 1.01,
            },
        )


def test_scenario_fit_rejects_non_numeric_capability():
    with pytest.raises(
        TypeError,
        match="Capability values must be int or float.",
    ):
        calculate_scenario_fit(
            demands=(),
            capabilities={
                StrategicDemand.MOBILITY: "high",
            },
        )


def test_scenario_fit_rejects_boolean_capability():
    with pytest.raises(
        TypeError,
        match="Capability values must be int or float.",
    ):
        calculate_scenario_fit(
            demands=(),
            capabilities={
                StrategicDemand.MOBILITY: True,
            },
        )

def test_scenario_fit_rejects_duplicate_demand_dimensions():
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
        calculate_scenario_fit(
            demands=demands,
            capabilities={
                StrategicDemand.MOBILITY: 0.5,
            },
        )

def test_scenario_definition_fit_uses_scenario_strategic_demands():
    scenario = ScenarioDefinition(
        id="TEST_SCENARIO",
        name="Test Scenario",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
        strategic_demands=(
            ScenarioDemand(
                dimension=StrategicDemand.MOBILITY,
                intensity=1.0,
            ),
            ScenarioDemand(
                dimension=StrategicDemand.DISTRIBUTED_CONTROL,
                intensity=0.5,
            ),
        ),
    )

    capabilities = {
        StrategicDemand.MOBILITY: 0.5,
        StrategicDemand.DISTRIBUTED_CONTROL: 0.5,
    }

    result = calculate_scenario_definition_fit(
        scenario=scenario,
        capabilities=capabilities,
    )

    assert result.score == pytest.approx(
        1.0 / 1.5,
    )


def test_scenario_definition_fit_returns_one_when_scenario_has_no_demands():
    scenario = ScenarioDefinition(
        id="TEST_SCENARIO",
        name="Test Scenario",
        pool=ScenarioPool.HOLD_OBJECTIVE,
        deployment_type=DeploymentType.STANDARD,
        termination_type=TerminationType.QUARTER_STRENGTH,
    )

    result = calculate_scenario_definition_fit(
        scenario=scenario,
        capabilities={},
    )

    assert result == ScenarioFitResult(
        score=1.0,
    )


def test_scenario_definition_fit_rejects_invalid_scenario():
    with pytest.raises(
        TypeError,
        match="scenario must be a ScenarioDefinition.",
    ):
        calculate_scenario_definition_fit(
            scenario="TEST_SCENARIO",
            capabilities={},
        )

def test_scenario_fit_from_profile_uses_capability_values():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=1.0,
        ),
        ScenarioDemand(
            dimension=StrategicDemand.PROJECTION,
            intensity=0.5,
        ),
    )

    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.5,
            ),
            ScenarioCapability(
                dimension=StrategicDemand.PROJECTION,
                value=0.5,
            ),
        ),
    )

    result = calculate_scenario_fit_from_profile(
        demands=demands,
        capability_profile=profile,
    )

    assert result.score == pytest.approx(
        1.0 / 1.5,
    )


def test_scenario_fit_from_profile_treats_absent_capability_as_zero():
    demands = (
        ScenarioDemand(
            dimension=StrategicDemand.MOBILITY,
            intensity=1.0,
        ),
    )

    profile = ScenarioCapabilityProfile()

    result = calculate_scenario_fit_from_profile(
        demands=demands,
        capability_profile=profile,
    )

    assert result == ScenarioFitResult(
        score=0.0,
    )


def test_scenario_fit_from_profile_returns_one_for_no_demands():
    result = calculate_scenario_fit_from_profile(
        demands=(),
        capability_profile=ScenarioCapabilityProfile(),
    )

    assert result == ScenarioFitResult(
        score=1.0,
    )


def test_scenario_fit_from_profile_rejects_invalid_profile():
    with pytest.raises(
        TypeError,
        match="capability_profile must be a ScenarioCapabilityProfile.",
    ):
        calculate_scenario_fit_from_profile(
            demands=(),
            capability_profile={},
        )