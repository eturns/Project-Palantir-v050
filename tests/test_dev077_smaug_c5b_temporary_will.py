"""DEV-077-SMAUG-C5B/E — shared Will grants, no Smaug-specific hardcoding."""
import pytest
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import OwnedResourceAllocation
from owned_resource_allocation_application import apply_owned_resource_allocations
from owned_resource_turn_transition import apply_owned_resource_turn
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from temporary_resource_grant import TemporaryResourceGrant


def state(name, will=0, might=0):
    owner=ResourceOwner(fielded_model_id=name)
    return OwnedHeroResourceState(owner, HeroResourceState(
        remaining_might=might,remaining_will=will,remaining_fate=0))


def cast(owner, points):
    return OwnedResourceAllocation(owner=owner, resource_type=ResourceType.WILL,
                                   resource_use=ResourceUse.CAST_SPELL, amount=points)


def grant(owner, points=1):
    return TemporaryResourceGrant(owner=owner, resource_type=ResourceType.WILL,
                                  amount=points)


def apply(states, allocations, grants=()):
    return apply_owned_resource_allocations(
        states=states, allocations=allocations, permissions=(),
        conversions=(),temporary_grants=grants)


def test_temporary_will_consumed_before_permanent_for_smaug():
    s=state("SMAUG:1",will=6)
    r=apply((s,), (cast(s.owner,1),), (grant(s.owner),))
    assert r[0].resources.remaining_will == 6
    assert s.resources.remaining_will == 6


def test_excess_spending_reduces_permanent_will_only_after_grant():
    s=state("SMAUG:1",will=6)
    r=apply((s,), (cast(s.owner,3),), (grant(s.owner),))
    assert r[0].resources.remaining_will == 4


def test_generic_other_model_same_mechanic():
    s=state("EXAMPLE_CASTER:1",will=2)
    r=apply((s,), (cast(s.owner,2),), (grant(s.owner,2),))
    assert r[0].resources.remaining_will == 2


def test_without_grant_cannot_spend_more_than_permanent():
    s=state("SMAUG:1",will=0)
    with pytest.raises(ValueError,match="exceed remaining Will"):
        apply((s,), (cast(s.owner,1),))


def test_grant_not_transferable_to_other_owner():
    a=state("SMAUG:1",will=0)
    b=state("OTHER:1",will=0)
    with pytest.raises(ValueError,match="exceed remaining Will"):
        apply((a,b),(cast(b.owner,1),),(grant(a.owner),))


def test_combined_allocations_do_not_reuse_temporary_point():
    s=state("SMAUG:1",will=0)
    allocations=(cast(s.owner,1),
        OwnedResourceAllocation(s.owner,ResourceType.WILL,ResourceUse.RESIST_MAGIC,1))
    with pytest.raises(ValueError,match="exceed remaining Will"):
        apply((s,),allocations,(grant(s.owner),))


def test_unused_grant_not_carried_into_following_turn():
    s=state("SMAUG:1",will=0)
    after=apply_owned_resource_turn(states=(s,),allocations=(),
        permissions=(),conversions=(),temporary_grants=(grant(s.owner),))
    with pytest.raises(ValueError,match="exceed remaining Will"):
        apply_owned_resource_turn(states=after,allocations=(cast(s.owner,1),),
            permissions=(),conversions=(),temporary_grants=())


def test_might_and_fate_unchanged_when_spending_temporary_will():
    s=state("SMAUG:1",will=6,might=3)
    r=apply((s,), (cast(s.owner,1),), (grant(s.owner),))
    assert r[0].resources.remaining_might == 3
    assert r[0].resources.remaining_fate == 0


def test_permanent_will_spent_as_before_without_grant():
    s=state("OTHER:1",will=4)
    r=apply((s,), (cast(s.owner,2),))
    assert r[0].resources.remaining_will == 2
