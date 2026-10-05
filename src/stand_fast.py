from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from profile_classification import HeroicStatus
from stand_fast_eligibility import (
    can_provide_stand_fast,
)
from command_benefit_eligibility import (
    can_receive_command_benefit,
)
from effective_special_rule_ids import (
    get_effective_special_rule_ids,
)

@dataclass(frozen=True)
class StandFastContext:
    distance_inches: float
    has_line_of_sight: bool

    def __post_init__(self) -> None:
        if self.distance_inches < 0:
            raise ValueError(
                "Stand Fast distance cannot be negative."
            )


GENERAL_OF_THE_NORTH_RULE_ID = (
    "GENERAL_OF_THE_NORTH"
)


def get_stand_fast_range_inches(
    provider: ConfiguredProfile | FieldedModelFormState,
) -> float:
    rule_ids = get_effective_special_rule_ids(
        provider
    )

    if GENERAL_OF_THE_NORTH_RULE_ID in rule_ids:
        return 12.0

    return 6.0


def can_receive_stand_fast_from_provider(
    provider: ConfiguredProfile | FieldedModelFormState,
    recipient: ConfiguredProfile | FieldedModelFormState,
) -> bool:
    if isinstance(
        recipient,
        FieldedModelFormState,
    ):
        recipient_profile = (
            recipient.active_configured_profile
        )
    else:
        recipient_profile = recipient

    if (
        recipient_profile.effective_heroic_status
        is HeroicStatus.WARRIOR
    ):
        return True

    provider_rule_ids = (
        get_effective_special_rule_ids(
            provider
        )
    )

    if (
        GENERAL_OF_THE_NORTH_RULE_ID
        in provider_rule_ids
        and recipient_profile.effective_heroic_status
        is HeroicStatus.HERO
        and "ORC"
        in recipient_profile.profile.races
    ):
        return True

    return False

def receives_stand_fast(
    provider: ConfiguredProfile | FieldedModelFormState,
    recipient: ConfiguredProfile | FieldedModelFormState,
    provider_passed_broken_courage_test: bool,
    context: StandFastContext,
) -> bool:
    """
    Returns whether a recipient automatically passes its
    Broken-Army Courage Test through Stand Fast.
    """

    if not provider_passed_broken_courage_test:
        return False

    if not can_provide_stand_fast(provider):
        return False

    if not can_receive_command_benefit(
        provider,
        recipient,
    ):
        return False

    if not can_provide_stand_fast(provider):
        return False

    if (
        context.distance_inches
        > get_stand_fast_range_inches(provider)
    ):
        return False

    if not context.has_line_of_sight:
        return False

    if isinstance(
        recipient,
        FieldedModelFormState,
    ):
        recipient_profile = (
            recipient.active_configured_profile
        )
    else:
        recipient_profile = recipient

    return can_receive_stand_fast_from_provider(
        provider,
        recipient,
    )