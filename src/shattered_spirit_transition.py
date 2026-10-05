from shattered_spirit_state import (
    ShatteredSpiritResult,
    ShatteredSpiritState,
)


def resolve_shattered_spirit(
    *,
    first_die: int,
    second_die: int,
    intelligence: str,
) -> ShatteredSpiritState:
    if not 1 <= first_die <= 6:
        raise ValueError(
            "first_die must be between 1 and 6."
        )

    if not 1 <= second_die <= 6:
        raise ValueError(
            "second_die must be between 1 and 6."
        )

    try:
        target = int(
            intelligence.removesuffix("+")
        )
    except (AttributeError, ValueError):
        raise ValueError(
            "Intelligence value must be between 3+ and 10+."
        )

    if not 3 <= target <= 10:
        raise ValueError(
            "Intelligence value must be between 3+ and 10+."
        )

    total = first_die + second_die

    if total < target:
        return ShatteredSpiritState(
            result=(
                ShatteredSpiritResult.OPPONENT_CONTROLLED
            ),
        )

    if first_die == second_die:
        return ShatteredSpiritState(
            result=ShatteredSpiritResult.EMPOWERED,
        )

    return ShatteredSpiritState(
        result=ShatteredSpiritResult.NORMAL,
    )