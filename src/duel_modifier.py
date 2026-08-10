from dataclasses import dataclass


@dataclass(frozen=True)
class DuelModifier:
    value: int = 0
    ignored_on_natural_six: bool = False

def apply_duel_modifier(
    natural_roll: int,
    modifier: DuelModifier,
) -> int:
    if not 1 <= natural_roll <= 6:
        raise ValueError(
            "Natural Duel roll must be between 1 and 6."
        )

    if (
        modifier.ignored_on_natural_six
        and natural_roll == 6
    ):
        return 6

    modified_roll = natural_roll + modifier.value

    return max(
        1,
        min(6, modified_roll),
    )

def apply_duel_modifier_to_rolls(
    rolls: tuple[int, ...],
    modifier: DuelModifier,
) -> tuple[int, ...]:
    return tuple(
        apply_duel_modifier(
            natural_roll=roll,
            modifier=modifier,
        )
        for roll in rolls
    )