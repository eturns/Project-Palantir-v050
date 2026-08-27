from scenario_capability import (
    ScenarioCapability,
)
from scenario_demand import (
    StrategicDemand,
)
from combat_benchmark import CombatBenchmark
from profiles import Profile
from staying_power_capability import (
    calculate_staying_power_from_profile,
)

def calculate_key_model_preservation_capability(
    defensive_survivability: int | float,
    protective_resources: int | float,
) -> ScenarioCapability:
    inputs = (
        defensive_survivability,
        protective_resources,
    )

    if any(
        (
            not isinstance(value, (int, float))
            or isinstance(value, bool)
        )
        for value in inputs
    ):
        raise TypeError(
            "capability inputs must be int or float."
        )

    if any(
        not 0.0 <= value <= 1.0
        for value in inputs
    ):
        raise ValueError(
            "capability inputs must be between 0.0 and 1.0."
        )

    value = (
        defensive_survivability
        + protective_resources
    ) / 2

    return ScenarioCapability(
        dimension=StrategicDemand.KEY_MODEL_PRESERVATION,
        value=value,
    )

def calculate_key_model_preservation_from_profile(
    profile: Profile,
    benchmark: CombatBenchmark,
    benchmark_fate: int | float,
) -> ScenarioCapability:
    if not isinstance(profile, Profile):
        raise TypeError(
            "profile must be a Profile."
        )

    if not isinstance(
        benchmark,
        CombatBenchmark,
    ):
        raise TypeError(
            "benchmark must be a CombatBenchmark."
        )

    if (
        not isinstance(benchmark_fate, (int, float))
        or isinstance(benchmark_fate, bool)
    ):
        raise TypeError(
            "benchmark_fate must be int or float."
        )

    if benchmark_fate <= 0:
        raise ValueError(
            "benchmark_fate must be greater than zero."
        )

    defensive_survivability = (
        calculate_staying_power_from_profile(
            profile=profile,
            benchmark=benchmark,
        )
    )

    protective_resources = min(
        profile.fate / benchmark_fate,
        1.0,
    )

    return calculate_key_model_preservation_capability(
        defensive_survivability=defensive_survivability,
        protective_resources=protective_resources,
    )