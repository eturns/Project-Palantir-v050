from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from runtime_special_rules import (
    get_runtime_granted_rule_ids,
)
from torturer_state import TorturerState

def get_effective_special_rule_ids(
    combatant: ConfiguredProfile | FieldedModelFormState,
    *,
    torturer_state: TorturerState | None = None,
) -> frozenset[str]:
    """
    Returns special-rule IDs currently available to the model,
    including rules inherited from an active Mount.
    """

    if isinstance(
        combatant,
        FieldedModelFormState,
    ):
        configured_profile = (
            combatant.active_configured_profile
        )

        mount_active = (
            combatant.has_active_mount
        )
    else:
        configured_profile = combatant
        mount_active = (
            configured_profile.effective_mount
            is not None
        )

    rule_ids = {
        assignment.rule.id
        for assignment
        in configured_profile.effective_special_rules
    }

    if (
        mount_active
        and configured_profile.effective_mount
        is not None
    ):
        rule_ids.update(
            configured_profile
            .effective_mount
            .special_rule_ids
        )

    static_rule_ids = frozenset(rule_ids)

    rule_ids.update(
        get_runtime_granted_rule_ids(
            static_rule_ids,
            torturer_state=torturer_state,
        )
    )

    return frozenset(rule_ids)