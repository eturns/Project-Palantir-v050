"""DEV-077-SMAUG-C5F: generic, immutable, per-turn temporary resource ledger.

Edward Turns (Project Lead)

Opt-in wrapper around existing owned resource validation and spending.
All allocations in one turn MUST pass the returned ledger to the next event.
Temporary grants are issued once at turn creation and cannot be reissued
through this API during the same turn. Ratings/army totals unaffected.
"""
from dataclasses import dataclass

from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import OwnedResourceAllocation
from owned_resource_allocation_application import apply_owned_resource_allocations
from owned_resource_allocation_totals import calculate_owned_resource_allocation_totals
from owned_resource_conversion import OwnedResourceConversion
from owned_resource_use_permission import OwnedResourceUsePermission
from resource_owner import ResourceOwner
from resource_use_permission import ResourceType
from temporary_resource_grant import TemporaryResourceGrant


@dataclass(frozen=True)
class TemporaryResourceTurnLedger:
    turn_number: int
    states: tuple[OwnedHeroResourceState, ...]
    grants: tuple[TemporaryResourceGrant, ...]
    spent: tuple[TemporaryResourceGrant, ...] = ()

    def remaining(self, owner: ResourceOwner, resource_type: ResourceType) -> int:
        allowed = sum(g.amount for g in self.grants
                      if g.owner == owner and g.resource_type == resource_type)
        used = sum(g.amount for g in self.spent
                   if g.owner == owner and g.resource_type == resource_type)
        return allowed - used


def _validate_initial(states, grants, turn_number):
    if type(turn_number) is not int or turn_number < 1:
        raise ValueError('turn_number must be a positive integer')
    if not isinstance(states, tuple) or not all(isinstance(s, OwnedHeroResourceState) for s in states):
        raise TypeError('states must be a tuple of OwnedHeroResourceState')
    owners = [s.owner for s in states]
    if len(owners) != len(set(owners)):
        raise ValueError('duplicate resource owners')
    if not isinstance(grants, tuple) or not all(isinstance(g, TemporaryResourceGrant) for g in grants):
        raise TypeError('grants must be a tuple of TemporaryResourceGrant')
    if any(g.owner not in owners for g in grants):
        raise ValueError('temporary grant owner must have a resource state')


def begin_temporary_resource_turn(
    *, states: tuple[OwnedHeroResourceState, ...],
    grants: tuple[TemporaryResourceGrant, ...] = (), turn_number: int = 1,
) -> TemporaryResourceTurnLedger:
    _validate_initial(states, grants, turn_number)
    return TemporaryResourceTurnLedger(turn_number, states, grants)


def apply_temporary_resource_event(
    ledger: TemporaryResourceTurnLedger, *,
    allocations: tuple[OwnedResourceAllocation, ...],
    permissions: tuple[OwnedResourceUsePermission, ...] = (),
    conversions: tuple[OwnedResourceConversion, ...] = (),
) -> TemporaryResourceTurnLedger:
    """Spend temporary pools first, then permanent pools; return a NEW ledger.

    Pass the returned ledger into the next event. Existing validation checks
    permissions, resource conversions and combined allocations per event.
    """
    if not isinstance(ledger, TemporaryResourceTurnLedger):
        raise TypeError('ledger must be TemporaryResourceTurnLedger')
    if not isinstance(allocations, tuple):
        raise TypeError('allocations must be a tuple')

    remaining_grants = tuple(
        TemporaryResourceGrant(g.owner, g.resource_type, ledger.remaining(g.owner, g.resource_type))
        for g in ledger.grants
        if ledger.remaining(g.owner, g.resource_type) > 0
    )
    # Merge duplicate source grants to avoid multiplying the same remainder.
    remaining_grants = tuple(
        TemporaryResourceGrant(owner, resource, ledger.remaining(owner, resource))
        for owner, resource in dict.fromkeys((g.owner, g.resource_type) for g in remaining_grants)
    )
    updated_states = apply_owned_resource_allocations(
        states=ledger.states, allocations=allocations,
        permissions=permissions, conversions=conversions,
        temporary_grants=remaining_grants,
    )
    totals = calculate_owned_resource_allocation_totals(allocations)
    used_this_event = tuple(
        TemporaryResourceGrant(owner, resource_type,
                               min(amount, ledger.remaining(owner, resource_type)))
        for (owner, resource_type), amount in totals.items()
        if resource_type in (ResourceType.MIGHT, ResourceType.WILL)
        and amount > 0 and ledger.remaining(owner, resource_type) > 0
    )
    return TemporaryResourceTurnLedger(
        ledger.turn_number, updated_states, ledger.grants,
        ledger.spent + used_this_event,
    )


def advance_temporary_resource_turn(
    ledger: TemporaryResourceTurnLedger, *,
    next_turn_number: int,
    grants: tuple[TemporaryResourceGrant, ...] = (),
) -> TemporaryResourceTurnLedger:
    """Expire all unspent temporary resources; carry only permanent states."""
    if not isinstance(ledger, TemporaryResourceTurnLedger):
        raise TypeError('ledger must be TemporaryResourceTurnLedger')
    if type(next_turn_number) is not int or next_turn_number != ledger.turn_number + 1:
        raise ValueError('next turn number must increase by exactly one')
    return begin_temporary_resource_turn(
        states=ledger.states, grants=grants, turn_number=next_turn_number,
    )
