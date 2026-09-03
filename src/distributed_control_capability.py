from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand
from profiles import Profile


def calculate_distributed_control_capability(
    scenario_presence: int | float,
    benchmark_presence: int | float,
) -> ScenarioCapability:
    if (
        not isinstance(scenario_presence, (int, float))
        or isinstance(scenario_presence, bool)
    ):
        raise TypeError(
            "scenario_presence must be int or float."
        )

    if (
        not isinstance(benchmark_presence, (int, float))
        or isinstance(benchmark_presence, bool)
    ):
        raise TypeError(
            "benchmark_presence must be int or float."
        )

    if scenario_presence < 0:
        raise ValueError(
            "scenario_presence cannot be negative."
        )

    if benchmark_presence <= 0:
        raise ValueError(
            "benchmark_presence must be greater than zero."
        )

    value = (
        scenario_presence
        / (
            scenario_presence
            + benchmark_presence
        )
    )

    return ScenarioCapability(
        dimension=StrategicDemand.DISTRIBUTED_CONTROL,
        value=value,
    )


def calculate_distributed_control_from_profiles(
    profiles: tuple[Profile, ...],
    benchmark_presence: int | float,
) -> ScenarioCapability:
    for profile in profiles:
        if not isinstance(profile, Profile):
            raise TypeError(
                "profiles must contain only Profile values."
            )

    physical_model_count = len(
        profiles,
    )

    return calculate_distributed_control_capability(
        scenario_presence=physical_model_count,
        benchmark_presence=benchmark_presence,
    )