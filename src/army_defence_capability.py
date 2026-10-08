"""DEV-077S-I2-C-H2: Generic army Defence capability.

Aggregates mechanical defensive survivability from
configured models in any army.

Provides:
- Average defensive combat capability per model
- Defensive output density per 100 army points

Resurrection is optional, with one assumed recovery
opportunity using the existing profile Defence engine.

This module contains no faction-specific scoring logic.
"""

from army import Army
from combat_benchmark import (
    CombatBenchmark,
    DEFAULT_COMBAT_BENCHMARK,
)
from profile_defensive_combat_score import (
    calculate_profile_defensive_combat_score,
)


def _calculate_total_defensive_output(
    army: Army,
    benchmark: CombatBenchmark,
    *,
    engagements: int,
    include_resurrection: bool,
) -> float:
    """Calculate quantity-weighted defensive output.

    Only entries representing fielded models contribute.
    Selected model configurations are preserved.

    Necromancer proximity and Will expenditure are not
    assumed by the army-level calculator.
    """

    total_score = 0.0

    for entry in army.entries:
        if not entry.counts_as_model:
            continue

        profile_score = (
            calculate_profile_defensive_combat_score(
                entry.configured_profile,
                benchmark,
                engagements=engagements,
                include_resurrection=include_resurrection,
            )
        )

        total_score += (
            profile_score * entry.quantity
        )

    return total_score


def calculate_army_defensive_combat_score(
    army: Army,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    engagements: int = 3,
    include_resurrection: bool = True,
) -> float:
    """Return average mechanical Defence per fielded model.

    A higher value indicates a greater average probability
    of surviving the benchmark or, when resurrection is
    enabled, being present after an assumed recovery
    opportunity.
    """

    model_count = army.model_count()

    if model_count == 0:
        return 0.0

    total_score = _calculate_total_defensive_output(
        army,
        benchmark,
        engagements=engagements,
        include_resurrection=include_resurrection,
    )

    return total_score / model_count


def calculate_army_defensive_output_density(
    army: Army,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    engagements: int = 3,
    include_resurrection: bool = True,
) -> float:
    """Return mechanical Defence output per 100 army points.

    Uses the army's actual configured points cost,
    including purchase points and other army costs.

    No additional bonuses are assigned to special-rule
    names or faction identities.
    """

    army_points = army.total_points()

    if army_points <= 0:
        return 0.0

    total_score = _calculate_total_defensive_output(
        army,
        benchmark,
        engagements=engagements,
        include_resurrection=include_resurrection,
    )

    return (
        total_score
        * 100.0
        / army_points
    )
