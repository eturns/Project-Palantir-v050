from dataclasses import dataclass

from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from profile_classification import HeroicStatus
from stand_fast_eligibility import (
    can_provide_stand_fast,
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

    if context.distance_inches > 6:
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

    return (
        recipient_profile.effective_heroic_status
        is HeroicStatus.WARRIOR
    )