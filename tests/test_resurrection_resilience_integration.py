import pytest

from resurrection_probability import (
    get_resurrection_probability_with_necromancer_will,
    get_resurrection_success_probability,
)
from resurrection_recovery import (
    calculate_expected_resurrection_bonus,
)
from resurrection_resilience_modifier import (
    calculate_resurrection_resilience_modifier,
)
from resurrection_state_resilience import (
    apply_resurrection_to_state_resilience,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_base_unholy_resurrection_pipeline_modifies_state_resilience():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    success_probability = (
        get_resurrection_success_probability()
    )

    expected_bonus = (
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=5,
            starting_models=10,
            success_probability=success_probability,
        )
    )

    resilience_modifier = (
        calculate_resurrection_resilience_modifier(
            expected_resurrection_bonus=expected_bonus,
            resilience_weight=0.5,
        )
    )

    result = apply_resurrection_to_state_resilience(
        state_resilience=baseline,
        resurrection_modifier=resilience_modifier,
    )

    assert float(success_probability) == pytest.approx(
        2 / 3,
    )

    assert expected_bonus == pytest.approx(
        1 / 3,
    )

    assert resilience_modifier == pytest.approx(
        1 / 6,
    )

    assert result.value == pytest.approx(
        0.6 + (1 / 6),
    )

def test_master_of_the_nazgul_improves_resurrection_resilience():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    success_probability = (
        get_resurrection_probability_with_necromancer_will(
            necromancer_remaining_will=20,
            distance_inches=6.0,
            will_points_available_to_spend=0,
        )
    )

    expected_bonus = (
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=5,
            starting_models=10,
            success_probability=success_probability,
        )
    )

    resilience_modifier = (
        calculate_resurrection_resilience_modifier(
            expected_resurrection_bonus=expected_bonus,
            resilience_weight=0.5,
        )
    )

    result = apply_resurrection_to_state_resilience(
        state_resilience=baseline,
        resurrection_modifier=resilience_modifier,
    )

    assert float(success_probability) == pytest.approx(
        5 / 6,
    )

    assert expected_bonus == pytest.approx(
        5 / 12,
    )

    assert resilience_modifier == pytest.approx(
        5 / 24,
    )

    assert result.value == pytest.approx(
        0.6 + (5 / 24),
    )


def test_necromancer_will_can_raise_supported_resurrection_to_certainty():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    success_probability = (
        get_resurrection_probability_with_necromancer_will(
            necromancer_remaining_will=20,
            distance_inches=6.0,
            will_points_available_to_spend=1,
        )
    )

    expected_bonus = (
        calculate_expected_resurrection_bonus(
            resurrection_capable_models=5,
            starting_models=10,
            success_probability=success_probability,
        )
    )

    resilience_modifier = (
        calculate_resurrection_resilience_modifier(
            expected_resurrection_bonus=expected_bonus,
            resilience_weight=0.5,
        )
    )

    result = apply_resurrection_to_state_resilience(
        state_resilience=baseline,
        resurrection_modifier=resilience_modifier,
    )

    assert float(success_probability) == 1.0

    assert expected_bonus == pytest.approx(
        0.5,
    )

    assert resilience_modifier == pytest.approx(
        0.25,
    )

    assert result.value == pytest.approx(
        0.85,
    )