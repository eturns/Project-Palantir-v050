from cavalry_charge import (
    qualifies_for_cavalry_charge_bonus,
)
from combat_context import CombatContext
from configured_profile import ConfiguredProfile
from fielded_model_form_state import (
    FieldedModelFormState,
)
from profile_classification import ModelType


def can_be_knocked_to_ground(
    defender: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
) -> bool:
    """
    Returns whether the defender is eligible to be
    knocked Prone by a Cavalry Charge.
    """

    if isinstance(
        defender,
        FieldedModelFormState,
    ):
        model_types = defender.effective_model_types
        strength = defender.effective_strength
    else:
        model_types = defender.effective_model_types
        strength = defender.effective_strength

    if ModelType.INFANTRY not in model_types:
        return False

    if ModelType.MONSTER in model_types:
        return False

    if strength >= 6:
        return False

    return True


def cavalry_charge_knocks_down(
    attacker: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
    defender: (
        ConfiguredProfile
        | FieldedModelFormState
    ),
    context: CombatContext,
    *,
    attacker_won_duel: bool,
) -> bool:
    """
    Returns whether this defender is knocked Prone
    by the attacker's Cavalry Charge.
    """

    if not attacker_won_duel:
        return False

    if not qualifies_for_cavalry_charge_bonus(
        attacker,
        context,
    ):
        return False

    return can_be_knocked_to_ground(
        defender
    )