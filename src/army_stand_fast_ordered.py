"""DEV-077S-I2-E-B5-B3: ordered Stand Fast expectation.

Uses validated contact distances/LOS and the existing eligibility resolver.
Calculates exact expectations over Hero test outcomes; Warriors do not
become Stand Fast providers. Activation order is an explicit input and
is not inferred from list order. Does not simulate casualties or movement.
"""
from dataclasses import dataclass
from fractions import Fraction

from army_broken_courage_resilience import BrokenCourageResilience
from army_stand_fast_integration import CourageSurvivor, StandFastContact
from contextual_courage import calculate_contextual_courage_success_probability
from profile_classification import HeroicStatus
from stand_fast import StandFastContext, receives_stand_fast
from fielded_model_form_state import FieldedModelFormState


@dataclass(frozen=True)
class OrderedCourageSurvivor:
    survivor: CourageSurvivor
    activation_index: int


def _hero(survivor: CourageSurvivor) -> bool:
    combatant = survivor.combatant
    configured = (combatant.active_configured_profile
                  if isinstance(combatant, FieldedModelFormState) else combatant)
    return configured.effective_heroic_status is HeroicStatus.HERO


def calculate_ordered_stand_fast_resilience(
    survivors: tuple[OrderedCourageSurvivor, ...] | list[OrderedCourageSurvivor],
    *,
    army_is_broken: bool,
    contacts: tuple[StandFastContact, ...] | list[StandFastContact] = (),
) -> BrokenCourageResilience:
    """Evaluate one specified activation sequence for the surviving force.

    Heroes activate with exact conditional pass chances, branching on their
    success/failure. This preserves correlations between an earlier Hero's
    Stand Fast and a later eligible Hero's provider outcome. Warriors are
    accumulated as expectations without branching, because they cannot
    provide Stand Fast. All survivors are assumed eligible to activate.
    """
    ordered = tuple(sorted(survivors, key=lambda x: x.activation_index))
    indices = [item.activation_index for item in ordered]
    if any(type(i) is not int or i < 0 for i in indices) or len(set(indices)) != len(indices):
        raise ValueError("Activation indices must be distinct non-negative integers")
    identities = [item.survivor.model_id for item in ordered]
    if any(not isinstance(i, str) or not i.strip() for i in identities) or len(set(identities)) != len(identities):
        raise ValueError("Survivors require unique non-empty model IDs")
    by_id = {item.survivor.model_id: item for item in ordered}
    count = len(ordered)
    if not army_is_broken:
        return BrokenCourageResilience(count, Fraction(count), Fraction(0),
                                       Fraction(1) if count else Fraction(0), False)

    eligible: dict[str, set[str]] = {i: set() for i in identities}
    for contact in contacts:
        if contact.provider_id not in by_id or contact.recipient_id not in by_id:
            raise ValueError("Stand Fast contact refers to an unknown survivor")
        if contact.provider_id == contact.recipient_id:
            raise ValueError("A model cannot provide Stand Fast to itself")
        provider = by_id[contact.provider_id]
        recipient = by_id[contact.recipient_id]
        # Always validate contacts, even if the provider is not a Hero.
        context = StandFastContext(contact.distance_inches, contact.has_line_of_sight)
        if provider.activation_index >= recipient.activation_index or not _hero(provider.survivor):
            continue
        if receives_stand_fast(provider.survivor.combatant,
                               recipient.survivor.combatant,
                               provider_passed_broken_courage_test=True,
                               context=context):
            eligible[contact.recipient_id].add(contact.provider_id)

    # Distribution over identities of Heroes that have passed so far.
    distribution: dict[frozenset[str], Fraction] = {frozenset(): Fraction(1)}
    expected = Fraction(0)
    for item in ordered:
        survivor = item.survivor
        individual = calculate_contextual_courage_success_probability(
            survivor.combatant,
            courage_context=survivor.courage_context,
            position_context=survivor.position_context,
        )
        next_distribution: dict[frozenset[str], Fraction] = {}
        for successful_heroes, mass in distribution.items():
            supported = bool(eligible[survivor.model_id] & successful_heroes)
            chance = Fraction(1) if supported else individual
            expected += mass * chance
            if _hero(survivor):
                success_set = successful_heroes | {survivor.model_id}
                next_distribution[success_set] = next_distribution.get(success_set, Fraction(0)) + mass * chance
                next_distribution[successful_heroes] = next_distribution.get(successful_heroes, Fraction(0)) + mass * (1 - chance)
            else:
                next_distribution[successful_heroes] = next_distribution.get(successful_heroes, Fraction(0)) + mass
        distribution = next_distribution
    return BrokenCourageResilience(
        surviving_model_count=count,
        expected_retained_models=expected,
        expected_fleeing_models=Fraction(count) - expected,
        retention_fraction=expected / count if count else Fraction(0),
        army_is_broken=True,
    )
