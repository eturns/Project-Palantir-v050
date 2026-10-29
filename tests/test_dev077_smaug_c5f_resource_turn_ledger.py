"""C5F: generic consecutive-event temporary Might/Will resource tests."""
import pytest
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import OwnedResourceAllocation
from owned_temporary_resource_turn_ledger import (
    begin_temporary_resource_turn, apply_temporary_resource_event,
    advance_temporary_resource_turn,
)
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from temporary_resource_grant import TemporaryResourceGrant


def setup(name='SMAUG:1:1', will=6, might=3, grants=((ResourceType.WILL, 1),)):
    owner = ResourceOwner(name)
    state = OwnedHeroResourceState(owner, HeroResourceState(
        remaining_might=might, remaining_will=will, remaining_fate=0))
    return begin_temporary_resource_turn(states=(state,), grants=tuple(
        TemporaryResourceGrant(owner, typ, amount) for typ, amount in grants))


def spend(ledger, amount=1, typ=ResourceType.WILL, use=ResourceUse.CAST_SPELL):
    return apply_temporary_resource_event(ledger, allocations=(
        OwnedResourceAllocation(ledger.states[0].owner, typ, use, amount),))


def test_first_event_uses_temporary_will_only():
    a = setup()
    b = spend(a)
    assert a.states[0].resources.remaining_will == 6
    assert b.states[0].resources.remaining_will == 6
    assert b.remaining(b.states[0].owner, ResourceType.WILL) == 0


def test_second_independent_event_spends_permanent_will():
    a = setup()
    b = spend(spend(a))
    assert b.states[0].resources.remaining_will == 5


def test_excess_second_event_rejected():
    a = setup(will=0)
    b = spend(a)
    with pytest.raises(ValueError, match='exceed remaining Will'):
        spend(b)


def test_two_different_will_uses_share_same_pool():
    a = setup()
    b = spend(a)
    c = spend(b, use=ResourceUse.RESIST_MAGIC)
    assert c.states[0].resources.remaining_will == 5


def test_mighty_hero_temporary_might_across_events():
    a = setup(grants=((ResourceType.MIGHT, 1),))
    b = spend(a, typ=ResourceType.MIGHT, use=ResourceUse.MODIFY_DUEL)
    c = spend(b, typ=ResourceType.MIGHT, use=ResourceUse.MODIFY_WOUND)
    assert b.states[0].resources.remaining_might == 3
    assert c.states[0].resources.remaining_might == 2


def test_expiry_and_fresh_next_turn_grant():
    a = setup(will=0)
    next_turn = advance_temporary_resource_turn(a, next_turn_number=2)
    with pytest.raises(ValueError, match='exceed remaining Will'):
        spend(next_turn)
    renewed = advance_temporary_resource_turn(a, next_turn_number=2,
        grants=(TemporaryResourceGrant(a.states[0].owner, ResourceType.WILL, 1),))
    assert spend(renewed).states[0].resources.remaining_will == 0


def test_cannot_restart_same_turn_through_advance():
    a = setup()
    with pytest.raises(ValueError, match='exactly one'):
        advance_temporary_resource_turn(a, next_turn_number=1)


def test_multiple_models_do_not_share_grants():
    a = setup(will=0)
    other = ResourceOwner('OTHER:1:1')
    second_state = OwnedHeroResourceState(other, HeroResourceState(0, 0, 0))
    ledger = begin_temporary_resource_turn(states=a.states + (second_state,), grants=a.grants)
    with pytest.raises(ValueError, match='exceed remaining Will'):
        apply_temporary_resource_event(ledger, allocations=(
            OwnedResourceAllocation(other, ResourceType.WILL, ResourceUse.CAST_SPELL, 1),))


def test_multiple_same_type_grants_not_double_counted():
    a = setup(will=0, grants=((ResourceType.WILL, 1),(ResourceType.WILL, 1)))
    b = spend(a)
    c = spend(b)
    with pytest.raises(ValueError, match='exceed remaining Will'):
        spend(c)
    assert c.remaining(c.states[0].owner, ResourceType.WILL) == 0


def test_original_grants_and_permanent_state_unchanged():
    a = setup()
    b = spend(a)
    assert a.spent == ()
    assert len(a.grants) == 1
    assert a.states[0].resources.remaining_will == 6
    assert b.grants == a.grants
