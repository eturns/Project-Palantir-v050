import pytest

from scenario_capability import ScenarioCapability
from scenario_capability_modifier import (
    apply_scenario_capability_modifier,
)
from scenario_demand import StrategicDemand


def test_positive_modifier_increases_capability():
    capability = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.6,
    )

    result = apply_scenario_capability_modifier(
        capability=capability,
        modifier=0.1,
    )

    assert result.dimension is StrategicDemand.STATE_RESILIENCE
    assert result.value == pytest.approx(0.7)


def test_negative_modifier_reduces_capability():
    capability = ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=0.6,
    )

    result = apply_scenario_capability_modifier(
        capability=capability,
        modifier=-0.2,
    )

    assert result.value == pytest.approx(0.4)


def test_positive_modifier_is_capped_at_one():
    capability = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.9,
    )

    result = apply_scenario_capability_modifier(
        capability=capability,
        modifier=0.3,
    )

    assert result.value == 1.0


def test_negative_modifier_is_capped_at_zero():
    capability = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.1,
    )

    result = apply_scenario_capability_modifier(
        capability=capability,
        modifier=-0.3,
    )

    assert result.value == 0.0


def test_modifier_must_be_numeric():
    capability = ScenarioCapability(
        dimension=StrategicDemand.STATE_RESILIENCE,
        value=0.5,
    )

    with pytest.raises(TypeError):
        apply_scenario_capability_modifier(
            capability=capability,
            modifier=True,
        )


def test_capability_must_be_scenario_capability():
    with pytest.raises(TypeError):
        apply_scenario_capability_modifier(
            capability=0.5,
            modifier=0.1,
        )