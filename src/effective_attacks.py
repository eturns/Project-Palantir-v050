from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from cavalry_charge import (
    qualifies_for_cavalry_charge_bonus,
)
from melee_weapon_selection import MeleeWeaponSelection
from morgul_blade_combat_values import (
    get_morgul_blade_combat_attacks,
)
from morgul_blade_state import MorgulBladeState

SAVAGE_HUNTERS_RULE_ID = "SAVAGE_HUNTERS"
KNIFE_FIGHTER_RULE_ID = "KNIFE_FIGHTER"
BLADE_MISTRESS_RULE_ID = "BLADE_MISTRESS"


def _configured_profile_from_combatant(
    combatant: ConfiguredProfile | FieldedModelFormState,
) -> ConfiguredProfile:
    if isinstance(
        combatant,
        FieldedModelFormState,
    ):
        return combatant.active_configured_profile

    return combatant


def get_effective_attacks(
    combatant: ConfiguredProfile | FieldedModelFormState,
    context: CombatContext,
    selection: MeleeWeaponSelection | None = None,
    morgul_blade_state: MorgulBladeState | None = None,
) -> int:
    """Number of Attacks available for this combat only.

    Knife Fighter / Blade Mistress require an explicit outnumbered flag
    and count of enemy models engaged with this particular model.
    Neither rule changes the underlying profile Attacks characteristic.
    """
    configured_profile = (
        _configured_profile_from_combatant(
            combatant
        )
    )

    attacks = get_morgul_blade_combat_attacks(
        combatant,
        selection=selection,
        state=morgul_blade_state,
    )

    special_rule_ids = {
        assignment.rule.id
        for assignment
        in configured_profile.effective_special_rules
    }

    if (
        SAVAGE_HUNTERS_RULE_ID in special_rule_ids
        and context.engagement_role
        is EngagementRole.CHARGED
    ):
        attacks += 1

    if qualifies_for_cavalry_charge_bonus(
        combatant,
        context,
    ):
        attacks += 1

    if context.outnumbered_in_combat is True:
        extra_enemies = max(0, context.engaged_enemy_models - 1)
        if KNIFE_FIGHTER_RULE_ID in special_rule_ids:
            attacks += min(3, extra_enemies)
        if BLADE_MISTRESS_RULE_ID in special_rule_ids:
            attacks += extra_enemies

    return attacks
