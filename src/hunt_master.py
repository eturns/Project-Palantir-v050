from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_profile import ConfiguredProfile
from fielded_model_form_state import (
    FieldedModelFormState,
)
from profile_classification import ModelType


HUNT_MASTER_RULE_ID = "HUNT_MASTER"


def _configured_profile_from_combatant(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
) -> ConfiguredProfile:
    if isinstance(
        combatant,
        FieldedModelFormState,
    ):
        return combatant.active_configured_profile

    return combatant


def has_hunt_master(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
) -> bool:
    configured_profile = (
        _configured_profile_from_combatant(
            combatant
        )
    )

    return any(
        assignment.rule.id
        == HUNT_MASTER_RULE_ID
        for assignment
        in configured_profile.effective_special_rules
    )


def hunt_master_allows_difficult_terrain_charge_bonus(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
    context: CombatContext,
) -> bool:
    return (
        has_hunt_master(combatant)
        and ModelType.CAVALRY
        in combatant.effective_model_types
        and context.engagement_role
        is EngagementRole.CHARGED
    )


def get_hunt_master_fight_bonus(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
    context: CombatContext,
) -> int:
    if (
        has_hunt_master(combatant)
        and ModelType.CAVALRY
        in combatant.effective_model_types
        and context.engagement_role
        is EngagementRole.CHARGED
    ):
        return 1

    return 0