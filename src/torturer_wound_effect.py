from torturer_state import TorturerState
from wound_attack_type import WoundAttackType
from wound_context import WoundContext
from wound_reroll import WoundReroll


def get_torturer_wound_reroll(
    state: TorturerState,
    context: WoundContext | None = None,
) -> WoundReroll:
    """
    Returns the To Wound reroll granted by Torturer
    for the current kill-count state.
    """

    attack_type = (
        context.attack_type
        if context is not None
        else WoundAttackType.STRIKE
    )

    if attack_type is not WoundAttackType.STRIKE:
        return WoundReroll()

    return WoundReroll(
        reroll_failed=(
            state.rerolls_all_failed_to_wound
        ),
        reroll_natural_ones=(
            state.rerolls_natural_ones_to_wound
        ),
    )