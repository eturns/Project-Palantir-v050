import pytest

from resurrection_resilience_calculator import (
    calculate_resurrection_modified_state_resilience,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_calculator_applies_base_resurrection_probability():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    result = calculate_resurrection_modified_state_resilience(
        state_resilience=baseline,
        resurrection_capable_models=5,
        starting_models=10,
        resilience_weight=0.5,
    )

    assert result.value == pytest.approx(
        0.6 + (1 / 6),
    )


def test_calculator_can_use_master_of_the_nazgul():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    result = calculate_resurrection_modified_state_resilience(
        state_resilience=baseline,
        resurrection_capable_models=5,
        starting_models=10,
        resilience_weight=0.5,
        necromancer_remaining_will=20,
        distance_inches=6.0,
        will_points_available_to_spend=0,
    )

    assert result.value == pytest.approx(
        0.6 + (5 / 24),
    )


def test_calculator_can_use_necromancer_will():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    result = calculate_resurrection_modified_state_resilience(
        state_resilience=baseline,
        resurrection_capable_models=5,
        starting_models=10,
        resilience_weight=0.5,
        necromancer_remaining_will=20,
        distance_inches=6.0,
        will_points_available_to_spend=1,
    )

    assert result.value == pytest.approx(
        0.85,
    )


def test_calculator_caps_final_state_resilience_at_one():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.9,
    )

    result = calculate_resurrection_modified_state_resilience(
        state_resilience=baseline,
        resurrection_capable_models=10,
        starting_models=10,
        resilience_weight=1.0,
    )

    assert result.value == 1.0