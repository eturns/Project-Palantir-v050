"""DEV-077S-I2-C-H3-B: Mechanical Defence diagnostics.

Produces combat-only and recovery-adjusted defensive
capabilities for any Army.

These values are diagnostic outputs, not calibrated
capability assessments.

No faction-specific or profile-specific scoring logic
is implemented here.
"""

from army import Army
from army_defence_capability import (
    calculate_army_defensive_combat_score,
    calculate_army_defensive_output_density,
)
from combat_benchmark import (
    CombatBenchmark,
    DEFAULT_COMBAT_BENCHMARK,
)


def calculate_mechanical_defence_diagnostics(
    army: Army,
    benchmark: CombatBenchmark = DEFAULT_COMBAT_BENCHMARK,
    *,
    engagements: int = 3,
) -> dict:
    """Return separate combat and recovery Defence metrics.

    combat_survival:
        Average probability of surviving the engagements.

    combat_density:
        Combat survivability output per 100 army points.

    recovery_presence:
        Average probability of presence after one assumed
        resurrection opportunity for eligible models.

    recovery_density:
        Recovery-adjusted output per 100 army points.

    The recovery calculation does not assume Necromancer
    support, favourable positioning or Will expenditure.
    """

    if (
        not isinstance(engagements, int)
        or isinstance(engagements, bool)
        or engagements < 1
    ):
        raise ValueError(
            "Engagements must be a positive integer."
        )

    combat_survival = (
        calculate_army_defensive_combat_score(
            army,
            benchmark,
            engagements=engagements,
            include_resurrection=False,
        )
    )

    combat_density = (
        calculate_army_defensive_output_density(
            army,
            benchmark,
            engagements=engagements,
            include_resurrection=False,
        )
    )

    recovery_presence = (
        calculate_army_defensive_combat_score(
            army,
            benchmark,
            engagements=engagements,
            include_resurrection=True,
        )
    )

    recovery_density = (
        calculate_army_defensive_output_density(
            army,
            benchmark,
            engagements=engagements,
            include_resurrection=True,
        )
    )

    return {
        "combat_survival": combat_survival,
        "combat_density": combat_density,
        "recovery_presence": recovery_presence,
        "recovery_density": recovery_density,
        "engagements": engagements,
    }
