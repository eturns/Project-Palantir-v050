import pytest

from hero_resource_state import HeroResourceState
from resource_allocation import ResourceAllocation
from resource_spend_domain import ResourceSpendDomain
from hero_hunting_resource_ledger import (
    ModelResourcePlan, evaluate_model_resource_plan, evaluate_army_resource_plans,
)


def plan(model_id="nec", *, might=2, will=3, fate=1, allocations=()):
    return ModelResourcePlan(model_id, HeroResourceState(might, will, fate), allocations)


def allocation(domain, might=0, will=0, fate=0):
    return ResourceAllocation(domain=domain, might=might, will=will, fate=fate)


def test_might_spent_in_combat_cannot_be_spent_again_in_magic():
    with pytest.raises(ValueError, match="Might exceeds"):
        evaluate_model_resource_plan(plan(
            might=1, allocations=(
                allocation(ResourceSpendDomain.COMBAT, might=1),
                allocation(ResourceSpendDomain.MAGIC, might=1),
            ),
        ))


def test_will_cast_and_resist_share_one_pool():
    with pytest.raises(ValueError, match="Will exceeds"):
        evaluate_model_resource_plan(plan(
            will=2, allocations=(
                allocation(ResourceSpendDomain.MAGIC, will=2),
                allocation(ResourceSpendDomain.DEFENCE, will=1),
            ),
        ))


def test_fate_shared_across_defensive_events():
    with pytest.raises(ValueError, match="Fate exceeds"):
        evaluate_model_resource_plan(plan(
            fate=1, allocations=(
                allocation(ResourceSpendDomain.DEFENCE, fate=1),
                allocation(ResourceSpendDomain.DEFENCE, fate=1),
            ),
        ))


def test_exact_resource_expenditure_allowed():
    result = evaluate_model_resource_plan(plan(
        might=1, will=2, fate=1, allocations=(
            allocation(ResourceSpendDomain.COMBAT, might=1),
            allocation(ResourceSpendDomain.MAGIC, will=1),
            allocation(ResourceSpendDomain.DEFENCE, will=1, fate=1),
        ),
    ))
    assert result.remaining == HeroResourceState(0, 0, 0)
    assert result.dashboard_score is None


def test_independent_models_keep_independent_pools():
    results = evaluate_army_resource_plans((
        plan("a", might=1, allocations=(allocation(ResourceSpendDomain.COMBAT, might=1),)),
        plan("b", might=1, allocations=(allocation(ResourceSpendDomain.COMBAT, might=1),)),
    ))
    assert len(results) == 2
    assert all(x.remaining.remaining_might == 0 for x in results)


def test_same_model_cannot_be_given_two_resource_budgets():
    with pytest.raises(ValueError, match="Duplicate resource budget"):
        evaluate_army_resource_plans((plan("a"),plan("a")))


def test_empty_plan_does_not_consume_resources():
    result = evaluate_model_resource_plan(plan())
    assert result.remaining == result.starting


def test_negative_resource_requests_rejected_by_existing_core():
    with pytest.raises(ValueError):
        allocation(ResourceSpendDomain.MAGIC, will=-1)


def test_blank_model_identity_rejected():
    with pytest.raises(ValueError, match="model_id"):
        evaluate_model_resource_plan(plan(" "))


def test_invalid_allocation_entry_rejected():
    with pytest.raises(TypeError, match="ResourceAllocation"):
        ModelResourcePlan("hero", HeroResourceState(1,1,1), ("not an allocation",))


def test_invalid_resource_state_rejected():
    with pytest.raises(TypeError, match="HeroResourceState"):
        ModelResourcePlan("hero", None, ())


def test_army_plans_must_be_tuple():
    with pytest.raises(TypeError, match="tuple"):
        evaluate_army_resource_plans([plan("hero")])
