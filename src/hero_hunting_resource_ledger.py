"""DEV-077S-I2-G2-E1: diagnostic-only cross-method resource ledger.

A single model's finite Might, Will and Fate are allocated once across
combat, magic and defence. This is an explicit plan, not a simulation of
conditional spending or dice outcomes. No legacy scoring is modified.
"""
from dataclasses import dataclass

from hero_resource_state import HeroResourceState
from resource_allocation import ResourceAllocation, apply_resource_allocations
from resource_spend_domain import ResourceSpendDomain


@dataclass(frozen=True)
class ModelResourcePlan:
    model_id: str
    starting: HeroResourceState
    allocations: tuple[ResourceAllocation, ...]

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id must be non-blank")
        if not isinstance(self.starting, HeroResourceState):
            raise TypeError("starting must be HeroResourceState")
        if not isinstance(self.allocations, tuple):
            raise TypeError("allocations must be a tuple")
        if not all(isinstance(a, ResourceAllocation) for a in self.allocations):
            raise TypeError("allocations must be ResourceAllocation entries")
        if not all(isinstance(a.domain, ResourceSpendDomain) for a in self.allocations):
            raise ValueError("resource domain must be supported")


@dataclass(frozen=True)
class ModelResourceEvidence:
    model_id: str
    starting: HeroResourceState
    remaining: HeroResourceState
    allocations: tuple[ResourceAllocation, ...]
    evidence_status: str = "explicit_resource_plan_only"
    dashboard_score: None = None
    scenario_score: None = None


def evaluate_model_resource_plan(plan: ModelResourcePlan) -> ModelResourceEvidence:
    remaining = apply_resource_allocations(plan.starting, plan.allocations)
    return ModelResourceEvidence(
        model_id=plan.model_id,
        starting=plan.starting,
        remaining=remaining,
        allocations=plan.allocations,
    )


def evaluate_army_resource_plans(
    plans: tuple[ModelResourcePlan, ...],
) -> tuple[ModelResourceEvidence, ...]:
    """Model IDs must be unique: never grant one hero several budgets."""
    if not isinstance(plans, tuple):
        raise TypeError("plans must be a tuple")
    seen = set()
    evidence = []
    for plan in plans:
        if not isinstance(plan, ModelResourcePlan):
            raise TypeError("each plan must be a ModelResourcePlan")
        if plan.model_id in seen:
            raise ValueError(f"Duplicate resource budget for model: {plan.model_id}")
        seen.add(plan.model_id)
        evidence.append(evaluate_model_resource_plan(plan))
    return tuple(evidence)
