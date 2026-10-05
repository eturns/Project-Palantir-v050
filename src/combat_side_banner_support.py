from banner_support import (
    has_banner_support,
)
from combat_side import CombatSide


def with_banner_support(
    side: CombatSide,
    *,
    banner_distances_inches: tuple[float, ...],
) -> CombatSide:
    return CombatSide(
        participants=side.participants,
        reroll_available=(
            side.reroll_available
            or has_banner_support(
                banner_distances_inches
            )
        ),
        might_user=side.might_user,
        might_available=side.might_available,
        might_strategy=side.might_strategy,
        heroic_strike_user=(
            side.heroic_strike_user
        ),
    )