from hero_resource_state import HeroResourceState


def spend_might(
    state: HeroResourceState,
    amount: int = 1,
) -> HeroResourceState:
    if amount < 0:
        raise ValueError(
            "Might spend amount cannot be negative."
        )

    if amount > state.remaining_might:
        raise ValueError(
            "Cannot spend more Might than remains."
        )

    return HeroResourceState(
        remaining_might=state.remaining_might - amount,
        remaining_will=state.remaining_will,
        remaining_fate=state.remaining_fate,
    )


def spend_will(
    state: HeroResourceState,
    amount: int = 1,
) -> HeroResourceState:
    if amount < 0:
        raise ValueError(
            "Will spend amount cannot be negative."
        )

    if amount > state.remaining_will:
        raise ValueError(
            "Cannot spend more Will than remains."
        )

    return HeroResourceState(
        remaining_might=state.remaining_might,
        remaining_will=state.remaining_will - amount,
        remaining_fate=state.remaining_fate,
    )


def spend_fate(
    state: HeroResourceState,
    amount: int = 1,
) -> HeroResourceState:
    if amount < 0:
        raise ValueError(
            "Fate spend amount cannot be negative."
        )

    if amount > state.remaining_fate:
        raise ValueError(
            "Cannot spend more Fate than remains."
        )

    return HeroResourceState(
        remaining_might=state.remaining_might,
        remaining_will=state.remaining_will,
        remaining_fate=state.remaining_fate - amount,
    )