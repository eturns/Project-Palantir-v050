from hero_resource_state import HeroResourceState


def regain_will(
    state: HeroResourceState,
    amount: int,
    starting_will: int,
) -> HeroResourceState:
    if amount < 0:
        raise ValueError(
            "Will recovery amount cannot be negative."
        )

    if starting_will < 0:
        raise ValueError(
            "Starting Will cannot be negative."
        )

    return HeroResourceState(
        remaining_might=state.remaining_might,
        remaining_will=min(
            starting_will,
            state.remaining_will + amount,
        ),
        remaining_fate=state.remaining_fate,
    )