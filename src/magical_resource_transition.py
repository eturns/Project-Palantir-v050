from dataclasses import dataclass

from hero_resource_spending import (
    spend_might,
    spend_will,
)
from hero_resource_state import HeroResourceState


@dataclass(frozen=True)
class MagicalResourceSpend:
    will: int = 0
    might: int = 0


def apply_magical_resource_spend(
    state: HeroResourceState,
    spend: MagicalResourceSpend,
) -> HeroResourceState:
    if spend.will < 0:
        raise ValueError(
            "Magical Will spend cannot be negative."
        )

    if spend.might < 0:
        raise ValueError(
            "Magical Might spend cannot be negative."
        )

    state_after_will = spend_will(
        state,
        amount=spend.will,
    )

    return spend_might(
        state_after_will,
        amount=spend.might,
    )