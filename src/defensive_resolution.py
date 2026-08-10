from defensive_state import DefensiveState
from strike_damage import (
    StrikeDamage,
    StrikeDamageType,
)
from post_prevention_effect import PostPreventionEffect

def apply_unprevented_wounds(
    state: DefensiveState,
    wounds: int,
) -> DefensiveState:
    if wounds < 0:
        raise ValueError(
            "Wounds to apply cannot be negative."
        )

    remaining_wounds = max(
        0,
        state.remaining_wounds - wounds,
    )

    return DefensiveState(
        remaining_wounds=remaining_wounds,
        remaining_fate=state.remaining_fate,
    )

def get_wounds_from_strike_damage(
    damage: StrikeDamage,
) -> int:
    if damage.damage_type != StrikeDamageType.FIXED:
        raise ValueError(
            "Only fixed StrikeDamage can be resolved deterministically."
        )

    return damage.wounds_per_successful_strike

def apply_post_prevention_effect(
    state: DefensiveState,
    effect: PostPreventionEffect,
) -> DefensiveState:
    if effect == PostPreventionEffect.NONE:
        return state

    if effect == PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO:
        return DefensiveState(
            remaining_wounds=0,
            remaining_fate=state.remaining_fate,
            remaining_will=state.remaining_will,
        )

    raise ValueError(
        "Unsupported post-prevention effect."
    )