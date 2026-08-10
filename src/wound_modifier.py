from dataclasses import dataclass


@dataclass(frozen=True)
class WoundModifier:
    to_wound: int = 0

def combine_wound_modifiers(
    modifiers: tuple[WoundModifier, ...],
) -> WoundModifier:
    return WoundModifier(
        to_wound=sum(
            modifier.to_wound
            for modifier in modifiers
        )
    )