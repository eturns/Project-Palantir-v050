"""DEV-077S-I2-E-B5-B2: position-explicit Stand Fast resilience adapter.

Converts actual configured/fielded models and validated positional contexts
into the B5-B1 probability contract. No army-wide coverage is inferred.
"""
from dataclasses import dataclass
from fractions import Fraction

from army_broken_courage_resilience import (
    BrokenCourageParticipant,
    BrokenCourageResilience,
    StandFastCoverage,
    calculate_broken_courage_resilience,
)
from configured_profile import ConfiguredProfile
from fielded_model_form_state import FieldedModelFormState
from profile_classification import HeroicStatus
from contextual_courage import (
    CouragePositionContext,
    calculate_contextual_courage_success_probability,
)
from courage_test import CourageTestContext
from stand_fast import StandFastContext, receives_stand_fast

Combatant = ConfiguredProfile | FieldedModelFormState


@dataclass(frozen=True)
class CourageSurvivor:
    model_id: str
    combatant: Combatant
    courage_context: CourageTestContext = CourageTestContext()
    position_context: CouragePositionContext = CouragePositionContext()


@dataclass(frozen=True)
class StandFastContact:
    provider_id: str
    recipient_id: str
    distance_inches: float
    has_line_of_sight: bool


def _configured(combatant: Combatant) -> ConfiguredProfile:
    if isinstance(combatant, FieldedModelFormState):
        return combatant.active_configured_profile
    return combatant


def calculate_positioned_broken_courage_resilience(
    survivors: tuple[CourageSurvivor, ...] | list[CourageSurvivor],
    *,
    army_is_broken: bool,
    contacts: tuple[StandFastContact, ...] | list[StandFastContact] = (),
) -> BrokenCourageResilience:
    """Calculate one broken activation window under explicitly supplied contacts.

    Contact records express observed distance/LOS, not assumed coverage.
    The B5-B1 engine handles shared and overlapping provider probabilities.
    Provider turn ordering and simultaneous activation are *not* modelled;
    callers must supply contacts for which a successful provider test could
    legally benefit the recipient. A hero cannot borrow Stand Fast from itself.
    """
    models = tuple(survivors)
    ids = [item.model_id for item in models]
    if any(not isinstance(i, str) or not i.strip() for i in ids):
        raise ValueError("Every survivor needs a non-empty model ID")
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate survivor model ID")
    by_id = {item.model_id: item for item in models}
    participants = tuple(
        BrokenCourageParticipant(
            model_id=item.model_id,
            individual_pass_probability=calculate_contextual_courage_success_probability(
                item.combatant,
                courage_context=item.courage_context,
                position_context=item.position_context,
            ),
            is_warrior=(
                _configured(item.combatant).effective_heroic_status
                is HeroicStatus.WARRIOR
            ),
        )
        for item in models
    )
    coverage = []
    for contact in contacts:
        if contact.provider_id not in by_id or contact.recipient_id not in by_id:
            raise ValueError("Stand Fast contact refers to an unknown survivor")
        provider = by_id[contact.provider_id]
        recipient = by_id[contact.recipient_id]
        if contact.provider_id == contact.recipient_id:
            raise ValueError("A model cannot provide Stand Fast to itself")
        if _configured(provider.combatant).effective_heroic_status is not HeroicStatus.HERO:
            continue
        context = StandFastContext(
            distance_inches=contact.distance_inches,
            has_line_of_sight=contact.has_line_of_sight,
        )
        if receives_stand_fast(
            provider.combatant,
            recipient.combatant,
            provider_passed_broken_courage_test=True,
            context=context,
        ):
            # The generic B5-B1 model supports standard Warrior recipients.
            # Special hero-recipient extensions must be modelled separately.
            if _configured(recipient.combatant).effective_heroic_status is HeroicStatus.WARRIOR:
                coverage.append(StandFastCoverage(contact.provider_id, contact.recipient_id))
    return calculate_broken_courage_resilience(
        participants,
        army_is_broken=army_is_broken,
        stand_fast_coverage=tuple(coverage),
    )
