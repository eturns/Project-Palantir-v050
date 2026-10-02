from dataclasses import replace

from morgul_blade_state import MorgulBladeState


def use_morgul_blade(
    state: MorgulBladeState,
) -> MorgulBladeState:
    """
    Declares use of the Morgul Blade for the current Combat.

    The Blade becomes permanently spent for the game, while
    remaining active until the current Combat has finished.
    """

    if state.used:
        raise ValueError(
            "Morgul Blade has already been used."
        )

    return replace(
        state,
        used=True,
        active_this_combat=True,
    )


def end_morgul_blade_combat(
    state: MorgulBladeState,
) -> MorgulBladeState:
    """
    Clears the current-Combat effect without making the
    Morgul Blade available again.
    """

    return replace(
        state,
        active_this_combat=False,
    )