from hero_resource_recovery import regain_will
from hero_resource_spending import spend_will
from hero_resource_state import HeroResourceState


def resolve_resistance_resources(
    state: HeroResourceState,
    starting_will: int,
    paid_resist_rolls: tuple[int, ...],
    free_resist_rolls: tuple[int, ...] = (),
) -> HeroResourceState:
    paid_will = len(paid_resist_rolls)

    state_after_spend = spend_will(
        state,
        amount=paid_will,
    )

    refund_count = sum(
        1
        for roll in paid_resist_rolls
        if roll == 6
    )

    return regain_will(
        state_after_spend,
        amount=refund_count,
        starting_will=starting_will,
    )