from combat_context import (
    CombatContext,
    EngagementRole,
)
from configured_profile import ConfiguredProfile
from fielded_model_form_state import (
    FieldedModelFormState,
)
from profile_classification import ModelType


def qualifies_for_cavalry_charge_bonus(
    combatant: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
    context: CombatContext,
) -> bool:
    """
    Returns whether the model qualifies for the
    standard Cavalry Charge bonuses in this combat.
    """

    if isinstance(
        combatant,
        FieldedModelFormState,
    ):
        model_types = (
            combatant.effective_model_types
        )
    else:
        model_types = (
            combatant.effective_model_types
        )

    if ModelType.CAVALRY not in model_types:
        return False

    if (
        context.engagement_role
        is not EngagementRole.CHARGED
    ):
        return False

    if not context.charged_only_infantry:
        return False

    if (
        not context
        .resolving_exclusively_against_infantry
    ):
        return False

    if context.in_difficult_terrain:
        return False

    if context.transfixed:
        return False

    if context.fighting_across_defended_barrier:
        return False

    return True