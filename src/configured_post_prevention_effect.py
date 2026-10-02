from configured_profile import ConfiguredProfile
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_effect import (
    get_morgul_blade_post_prevention_effect,
)
from morgul_blade_state import MorgulBladeState
from post_prevention_effect import (
    PostPreventionEffect,
)
from special_rule_post_prevention_effect import (
    get_special_rule_post_prevention_effect,
)
from wound_context import WoundContext


def get_configured_post_prevention_effect(
    attacker: ConfiguredProfile,
    *,
    selection: MeleeWeaponSelection | None = None,
    context: WoundContext,
    morgul_blade_state: MorgulBladeState | None = None,
) -> PostPreventionEffect:
    special_rule_effect = (
        get_special_rule_post_prevention_effect(
            attacker,
            context=context,
        )
    )

    if (
        special_rule_effect
        is not PostPreventionEffect.NONE
    ):
        return special_rule_effect

    if morgul_blade_state is not None:
        return get_morgul_blade_post_prevention_effect(
            attacker,
            selection=selection,
            state=morgul_blade_state,
            context=context,
        )

    return PostPreventionEffect.NONE