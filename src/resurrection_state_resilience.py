from scenario_capability import ScenarioCapability
from scenario_capability_modifier import (
    apply_scenario_capability_modifier,
)
from scenario_demand import StrategicDemand


def apply_resurrection_to_state_resilience(
    state_resilience: ScenarioCapability,
    resurrection_modifier: int | float,
) -> ScenarioCapability:
    if not isinstance(
        state_resilience,
        ScenarioCapability,
    ):
        raise TypeError(
            "state_resilience must be a ScenarioCapability."
        )

    if (
        state_resilience.dimension
        is not StrategicDemand.STATE_RESILIENCE
    ):
        raise ValueError(
            "state_resilience must use the STATE_RESILIENCE dimension."
        )

    if (
        not isinstance(resurrection_modifier, (int, float))
        or isinstance(resurrection_modifier, bool)
    ):
        raise TypeError(
            "resurrection_modifier must be int or float."
        )

    if not 0.0 <= resurrection_modifier <= 1.0:
        raise ValueError(
            "resurrection_modifier must be between 0.0 and 1.0."
        )

    return apply_scenario_capability_modifier(
        capability=state_resilience,
        modifier=resurrection_modifier,
    )