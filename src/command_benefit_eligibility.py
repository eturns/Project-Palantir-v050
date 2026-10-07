from configured_profile import ConfiguredProfile
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)
from fielded_model_form_state import (
    FieldedModelFormState,
)


PACK_MASTER_RULE_ID = "PACK_MASTER"


def can_receive_command_benefit(
    provider: ConfiguredProfile | FieldedModelFormState,
    recipient: ConfiguredProfile | FieldedModelFormState,
) -> bool:
    """
    Returns whether a recipient may benefit from a
    provider's command-style group effects.

    Individual systems such as Stand Fast or future
    Heroic Action consumers remain responsible for
    their own normal eligibility rules.
    """

    provider_rule_ids = (
        get_effective_special_rule_ids(
            provider
        )
    )

    if isinstance(
        recipient,
        FieldedModelFormState,
    ):
        recipient_profile = (
            recipient.active_configured_profile
        )
    else:
        recipient_profile = recipient

    if PACK_MASTER_RULE_ID in provider_rule_ids:
        return (
            "WARG"
            in recipient_profile.effective_keywords
        )

    return True