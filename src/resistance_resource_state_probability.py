from dataclasses import dataclass

from hero_resource_spending import spend_will
from hero_resource_state import HeroResourceState
from resistance_resource_probability import (
    resist_will_refund_distribution,
)


@dataclass(frozen=True)
class WeightedHeroResourceState:
    state: HeroResourceState
    probability: float


def resistance_resource_state_distribution(
    resources: HeroResourceState,
    paid_dice_count: int,
    starting_will: int,
) -> tuple[WeightedHeroResourceState, ...]:
    state_after_spend = spend_will(
        resources,
        amount=paid_dice_count,
    )

    refund_distribution = (
        resist_will_refund_distribution(
            paid_dice_count=paid_dice_count,
        )
    )

    outcomes = []

    for refund_count, probability in (
        refund_distribution.items()
    ):
        resulting_will = min(
            starting_will,
            state_after_spend.remaining_will
            + refund_count,
        )

        outcomes.append(
            WeightedHeroResourceState(
                state=HeroResourceState(
                    remaining_might=(
                        state_after_spend.remaining_might
                    ),
                    remaining_will=resulting_will,
                    remaining_fate=(
                        state_after_spend.remaining_fate
                    ),
                ),
                probability=probability,
            )
        )

    return tuple(outcomes)