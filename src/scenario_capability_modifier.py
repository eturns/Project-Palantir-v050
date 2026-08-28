from scenario_capability import ScenarioCapability


def apply_scenario_capability_modifier(
    capability: ScenarioCapability,
    modifier: int | float,
) -> ScenarioCapability:
    if not isinstance(
        capability,
        ScenarioCapability,
    ):
        raise TypeError(
            "capability must be a ScenarioCapability."
        )

    if (
        not isinstance(modifier, (int, float))
        or isinstance(modifier, bool)
    ):
        raise TypeError(
            "modifier must be int or float."
        )

    value = capability.value + modifier

    value = max(
        0.0,
        min(
            value,
            1.0,
        ),
    )

    return ScenarioCapability(
        dimension=capability.dimension,
        value=value,
    )