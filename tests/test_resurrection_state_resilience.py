import pytest

from resurrection_state_resilience import (
    apply_resurrection_to_state_resilience,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def test_resurrection_modifier_increases_state_resilience():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    result = apply_resurrection_to_state_resilience(
        state_resilience=baseline,
        resurrection_modifier=0.15,
    )

    assert result.dimension is StrategicDemand.STATE_RESILIENCE
    assert result.value == pytest.approx(0.75)


def test_resurrection_modifier_is_capped_at_one():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.9,
    )

    result = apply_resurrection_to_state_resilience(
        state_resilience=baseline,
        resurrection_modifier=0.2,
    )

    assert result.value == 1.0


def test_non_state_resilience_capability_is_rejected():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.6,
    )

    with pytest.raises(ValueError):
        apply_resurrection_to_state_resilience(
            state_resilience=baseline,
            resurrection_modifier=0.15,
        )


def test_resurrection_modifier_must_be_between_zero_and_one():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    with pytest.raises(ValueError):
        apply_resurrection_to_state_resilience(
            state_resilience=baseline,
            resurrection_modifier=1.1,
        )


def test_boolean_modifier_is_rejected():
    baseline = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    with pytest.raises(TypeError):
        apply_resurrection_to_state_resilience(
            state_resilience=baseline,
            resurrection_modifier=True,
        )