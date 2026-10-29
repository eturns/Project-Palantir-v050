"""C5C: Desolator Will grant uses shared temporary resource infrastructure."""
from hero_resource_state import HeroResourceState
from owned_hero_resource_state import OwnedHeroResourceState
from owned_resource_allocation import OwnedResourceAllocation
from owned_resource_turn_transition import apply_owned_resource_turn
from resource_owner import ResourceOwner
from resource_use import ResourceUse
from resource_use_permission import ResourceType
from special_rule_temporary_resource_grants import get_special_rule_temporary_resource_grants


def grants(owner, *rules):
    return get_special_rule_temporary_resource_grants(owner, frozenset(rules))


def test_smaug_desolator_generates_temporary_will():
    owner = ResourceOwner('SMAUG:1:1')
    result = grants(owner, 'DESOLATOR_OF_THE_NORTH')
    assert len(result) == 1
    assert result[0].resource_type == ResourceType.WILL
    assert result[0].amount == 1
    assert result[0].owner == owner


def test_rule_absent_does_not_grant():
    assert grants(ResourceOwner('SMAUG:1:1')) == ()


def test_other_owner_with_rule_reuses_same_mechanic():
    owner = ResourceOwner('FUTURE_CASTER:1:1')
    result = grants(owner, 'DESOLATOR_OF_THE_NORTH')
    assert len(result) == 1 and result[0].owner == owner


def test_mighty_hero_and_desolator_grant_different_resource_types():
    owner = ResourceOwner('TEST:1:1')
    result = grants(owner, 'MIGHTY_HERO', 'DESOLATOR_OF_THE_NORTH')
    assert {x.resource_type for x in result} == {ResourceType.MIGHT, ResourceType.WILL}


def test_duplicate_rule_ids_do_not_duplicate_grant():
    owner = ResourceOwner('SMAUG:1:1')
    result = grants(owner, 'DESOLATOR_OF_THE_NORTH', 'DESOLATOR_OF_THE_NORTH')
    assert len(result) == 1


def test_resource_consumed_without_decreasing_permanent_will():
    owner = ResourceOwner('SMAUG:1:1')
    state = OwnedHeroResourceState(owner, HeroResourceState(3,6,0))
    allocation = OwnedResourceAllocation(owner, ResourceType.WILL, ResourceUse.CAST_SPELL, 1)
    result = apply_owned_resource_turn((state,), (allocation,), (), (), grants(owner, 'DESOLATOR_OF_THE_NORTH'))
    assert result[0].resources.remaining_will == 6


def test_unused_grant_does_not_persist_into_next_turn():
    owner = ResourceOwner('SMAUG:1:1')
    state = OwnedHeroResourceState(owner, HeroResourceState(3,0,0))
    after = apply_owned_resource_turn((state,), (), (), (), grants(owner, 'DESOLATOR_OF_THE_NORTH'))
    assert after[0].resources.remaining_will == 0


def test_grant_cannot_spend_other_models_permanent_will():
    owner_a = ResourceOwner('SMAUG:1:1')
    owner_b = ResourceOwner('TEST:1:1')
    result = grants(owner_a, 'DESOLATOR_OF_THE_NORTH')
    assert all(x.owner != owner_b for x in result)
