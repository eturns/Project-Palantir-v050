import pytest

from scenario_fit import ScenarioFitResult
from scenario_demand import (
    ScenarioDemand,
    StrategicDemand,
)
from scenario_definition import (
    DeploymentType,
    ScenarioDefinition,
    ScenarioPool,
    TerminationType,
)
from scenario_pool_fit import (
    calculate_scenario_pool_fit,
    calculate_scenario_pool_fit_from_definitions,
    ScenarioPoolFitResult,
    ScenarioPoolFitSummary,
)
import scenario_pool_fit

from scenario_catalogue import (
    get_official_scenarios_by_pool,
)
from scenario_capability import (
    ScenarioCapability,
    ScenarioCapabilityProfile,
)
def test_scenario_pool_fit_is_mean_of_scenario_fit_scores():
    scenario_fits = (
        ScenarioFitResult(
            score=0.6,
        ),
        ScenarioFitResult(
            score=0.8,
        ),
        ScenarioFitResult(
            score=1.0,
        ),
    )

    result = calculate_scenario_pool_fit(
        scenario_fits=scenario_fits,
    )

    assert result == pytest.approx(
        0.8,
    )

def test_scenario_pool_fit_rejects_empty_scenario_fits():
    with pytest.raises(
        ValueError,
        match="scenario_fits cannot be empty.",
    ):
        calculate_scenario_pool_fit(
            scenario_fits=(),
        )

def test_scenario_pool_fit_rejects_invalid_scenario_fit_entries():
    with pytest.raises(
        TypeError,
        match="scenario_fits must contain only ScenarioFitResult values.",
    ):
        calculate_scenario_pool_fit(
            scenario_fits=(
                ScenarioFitResult(
                    score=0.8,
                ),
                0.6,
            ),
        )

def test_scenario_pool_fit_from_definitions_averages_scenario_fits():
    scenarios = (
        ScenarioDefinition(
            id="SCENARIO_ONE",
            name="Scenario One",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
            strategic_demands=(
                ScenarioDemand(
                    dimension=StrategicDemand.MOBILITY,
                    intensity=1.0,
                ),
            ),
        ),
        ScenarioDefinition(
            id="SCENARIO_TWO",
            name="Scenario Two",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
            strategic_demands=(
                ScenarioDemand(
                    dimension=StrategicDemand.MOBILITY,
                    intensity=0.5,
                ),
            ),
        ),
    )

    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    result = calculate_scenario_pool_fit_from_definitions(
        scenarios=scenarios,
        capabilities=capabilities,
    )

    assert result == pytest.approx(
        0.6,
    )

def test_scenario_pool_fit_from_definitions_rejects_empty_scenarios():
    with pytest.raises(
        ValueError,
        match="scenario_fits cannot be empty.",
    ):
        calculate_scenario_pool_fit_from_definitions(
            scenarios=(),
            capabilities={},
        )

def test_scenario_pool_fit_from_definitions_rejects_mixed_pools():
    scenarios = (
        ScenarioDefinition(
            id="SCENARIO_ONE",
            name="Scenario One",
            pool=ScenarioPool.HOLD_OBJECTIVE,
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
        ),
        ScenarioDefinition(
            id="SCENARIO_TWO",
            name="Scenario Two",
            pool=ScenarioPool.KILL_THE_ENEMY,
            deployment_type=DeploymentType.STANDARD,
            termination_type=TerminationType.QUARTER_STRENGTH,
        ),
    )

    with pytest.raises(
        ValueError,
        match="scenarios must all belong to the same pool.",
    ):
        calculate_scenario_pool_fit_from_definitions(
            scenarios=scenarios,
            capabilities={},
        )

def test_official_scenario_pool_fit_uses_official_scenarios_for_pool():
    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    scenarios = get_official_scenarios_by_pool(
        ScenarioPool.HOLD_OBJECTIVE,
    )

    expected = calculate_scenario_pool_fit_from_definitions(
        scenarios=scenarios,
        capabilities=capabilities,
    )

    result = scenario_pool_fit.calculate_official_scenario_pool_fit(
        pool=ScenarioPool.HOLD_OBJECTIVE,
        capabilities=capabilities,
    )

    assert result == pytest.approx(
        expected,
    )

def test_official_scenario_pool_fit_rejects_invalid_pool():
    with pytest.raises(
        TypeError,
        match="pool must be a ScenarioPool.",
    ):
        scenario_pool_fit.calculate_official_scenario_pool_fit(
            pool="hold_objective",
            capabilities={},
        )

def test_all_official_scenario_pool_fits_include_every_pool():
    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    result = scenario_pool_fit.calculate_all_official_scenario_pool_fits(
        capabilities=capabilities,
    )

    assert set(result) == set(ScenarioPool)

def test_all_official_scenario_pool_fits_match_individual_pool_results():
    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    result = scenario_pool_fit.calculate_all_official_scenario_pool_fits(
        capabilities=capabilities,
    )

    for pool in ScenarioPool:
        expected = scenario_pool_fit.calculate_official_scenario_pool_fit(
            pool=pool,
            capabilities=capabilities,
        )

        assert result[pool] == pytest.approx(
            expected,
        )

def test_scenario_pool_fit_result_stores_pool_and_score():
    result = ScenarioPoolFitResult(
        pool=ScenarioPool.HOLD_OBJECTIVE,
        score=0.75,
    )

    assert result.pool is ScenarioPool.HOLD_OBJECTIVE
    assert result.score == 0.75

def test_scenario_pool_fit_result_is_immutable():
    result = ScenarioPoolFitResult(
        pool=ScenarioPool.HOLD_OBJECTIVE,
        score=0.5,
    )

    with pytest.raises(AttributeError):
        result.score = 0.8


def test_scenario_pool_fit_result_rejects_invalid_pool():
    with pytest.raises(
        TypeError,
        match="pool must be a ScenarioPool.",
    ):
        ScenarioPoolFitResult(
            pool="hold_objective",
            score=0.5,
        )


def test_scenario_pool_fit_result_rejects_negative_score():
    with pytest.raises(
        ValueError,
        match="Scenario pool fit score must be between 0.0 and 1.0.",
    ):
        ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=-0.01,
        )


def test_scenario_pool_fit_result_rejects_score_above_one():
    with pytest.raises(
        ValueError,
        match="Scenario pool fit score must be between 0.0 and 1.0.",
    ):
        ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=1.01,
        )

def test_build_official_scenario_pool_fit_report_returns_structured_results():
    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    result = scenario_pool_fit.build_official_scenario_pool_fit_report(
        capabilities=capabilities,
    )

    assert len(result) == len(ScenarioPool)

    assert all(
        isinstance(
            pool_result,
            ScenarioPoolFitResult,
        )
        for pool_result in result
    )

    assert {
        pool_result.pool
        for pool_result in result
    } == set(ScenarioPool)

def test_official_scenario_pool_fit_report_matches_individual_pool_scores():
    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    report = scenario_pool_fit.build_official_scenario_pool_fit_report(
        capabilities=capabilities,
    )

    report_by_pool = {
        pool_result.pool: pool_result.score
        for pool_result in report
    }

    for pool in ScenarioPool:
        expected = scenario_pool_fit.calculate_official_scenario_pool_fit(
            pool=pool,
            capabilities=capabilities,
        )

        assert report_by_pool[pool] == pytest.approx(
            expected,
        )

def test_official_scenario_pool_fit_report_preserves_scenario_pool_order():
    report = scenario_pool_fit.build_official_scenario_pool_fit_report(
        capabilities={},
    )

    assert tuple(
        pool_result.pool
        for pool_result in report
    ) == tuple(ScenarioPool)

def test_build_official_scenario_pool_fit_report_from_profile_matches_mapping_report():
    profile = ScenarioCapabilityProfile(
        capabilities=(
            ScenarioCapability(
                dimension=StrategicDemand.MOBILITY,
                value=0.4,
            ),
        ),
    )

    expected = scenario_pool_fit.build_official_scenario_pool_fit_report(
        capabilities=profile.to_mapping(),
    )

    result = scenario_pool_fit.build_official_scenario_pool_fit_report_from_profile(
        capability_profile=profile,
    )

    assert result == expected

def test_get_strongest_scenario_pool_returns_highest_score():
    results = (
        ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.6,
        ),
        ScenarioPoolFitResult(
            pool=ScenarioPool.KILL_THE_ENEMY,
            score=0.8,
        ),
        ScenarioPoolFitResult(
            pool=ScenarioPool.MANOEUVRING,
            score=0.4,
        ),
    )

    result = scenario_pool_fit.get_strongest_scenario_pool(
        pool_results=results,
    )

    assert result == ScenarioPoolFitResult(
        pool=ScenarioPool.KILL_THE_ENEMY,
        score=0.8,
    )


def test_get_weakest_scenario_pool_returns_lowest_score():
    results = (
        ScenarioPoolFitResult(
            pool=ScenarioPool.HOLD_OBJECTIVE,
            score=0.6,
        ),
        ScenarioPoolFitResult(
            pool=ScenarioPool.KILL_THE_ENEMY,
            score=0.8,
        ),
        ScenarioPoolFitResult(
            pool=ScenarioPool.MANOEUVRING,
            score=0.4,
        ),
    )

    result = scenario_pool_fit.get_weakest_scenario_pool(
        pool_results=results,
    )

    assert result == ScenarioPoolFitResult(
        pool=ScenarioPool.MANOEUVRING,
        score=0.4,
    )

def test_get_strongest_scenario_pool_rejects_empty_results():
    with pytest.raises(
        ValueError,
        match="pool_results cannot be empty.",
    ):
        scenario_pool_fit.get_strongest_scenario_pool(
            pool_results=(),
        )


def test_get_weakest_scenario_pool_rejects_empty_results():
    with pytest.raises(
        ValueError,
        match="pool_results cannot be empty.",
    ):
        scenario_pool_fit.get_weakest_scenario_pool(
            pool_results=(),
        )

def test_build_official_scenario_pool_fit_summary_contains_report_and_extremes():
    capabilities = {
        StrategicDemand.MOBILITY: 0.4,
    }

    result = scenario_pool_fit.build_official_scenario_pool_fit_summary(
        capabilities=capabilities,
    )

    assert isinstance(
        result,
        ScenarioPoolFitSummary,
    )

    assert len(result.pool_results) == len(ScenarioPool)

    assert result.strongest == scenario_pool_fit.get_strongest_scenario_pool(
        pool_results=result.pool_results,
    )

    assert result.weakest == scenario_pool_fit.get_weakest_scenario_pool(
        pool_results=result.pool_results,
    )