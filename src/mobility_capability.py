from army import Army
from army_manoeuvrability import (
    calculate_army_manoeuvrability,
)
from scenario_capability import ScenarioCapability
from scenario_demand import StrategicDemand


def calculate_mobility_capability(
    manoeuvrability: int | float,
    benchmark_manoeuvrability: int | float,
) -> ScenarioCapability:
    if (
        not isinstance(manoeuvrability, (int, float))
        or isinstance(manoeuvrability, bool)
    ):
        raise TypeError(
            "manoeuvrability must be int or float."
        )

    if (
        not isinstance(
            benchmark_manoeuvrability,
            (int, float),
        )
        or isinstance(
            benchmark_manoeuvrability,
            bool,
        )
    ):
        raise TypeError(
            "benchmark_manoeuvrability must be int or float."
        )

    if manoeuvrability < 0:
        raise ValueError(
            "manoeuvrability cannot be negative."
        )

    if benchmark_manoeuvrability <= 0:
        raise ValueError(
            "benchmark_manoeuvrability must be greater than zero."
        )

    value = (
        manoeuvrability
        / (
            manoeuvrability
            + benchmark_manoeuvrability
        )
    )

    return ScenarioCapability(
        dimension=StrategicDemand.MOBILITY,
        value=value,
    )


def calculate_mobility_capability_from_army(
    army: Army,
    benchmark_manoeuvrability: int | float,
) -> ScenarioCapability:
    if not isinstance(army, Army):
        raise TypeError(
            "army must be an Army."
        )

    manoeuvrability = calculate_army_manoeuvrability(
        army,
    )

    return calculate_mobility_capability(
        manoeuvrability=manoeuvrability,
        benchmark_manoeuvrability=(
            benchmark_manoeuvrability
        ),
    )