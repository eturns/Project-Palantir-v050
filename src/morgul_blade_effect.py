from configured_profile import ConfiguredProfile
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_state import MorgulBladeState
from post_prevention_effect import PostPreventionEffect
from wound_attack_type import WoundAttackType
from wound_context import WoundContext


MORGUL_BLADE_WARGEAR_ID = "WG_MORGUL_BLADE"


def get_morgul_blade_post_prevention_effect(
    attacker: ConfiguredProfile,
    *,
    selection: MeleeWeaponSelection | None,
    state: MorgulBladeState,
    context: WoundContext | None = None,
) -> PostPreventionEffect:
    wargear_ids = {
        wargear.id
        for wargear in attacker.effective_wargear
    }

    if MORGUL_BLADE_WARGEAR_ID not in wargear_ids:
        return PostPreventionEffect.NONE

    if not state.active_this_combat:
        return PostPreventionEffect.NONE

    if (
        selection is None
        or selection.wargear_id
        != MORGUL_BLADE_WARGEAR_ID
    ):
        return PostPreventionEffect.NONE

    attack_type = (
        context.attack_type
        if context is not None
        else WoundAttackType.STRIKE
    )

    if attack_type is not WoundAttackType.STRIKE:
        return PostPreventionEffect.NONE

    return PostPreventionEffect.REDUCE_WOUNDS_TO_ZERO