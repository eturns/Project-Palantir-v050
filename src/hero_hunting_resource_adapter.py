"""DEV-077S-I2-G2-E2: explicit cross-method resource adapter.

Maps declared Melee, Shooting, Magic and defensive spends onto the E1 ledger.
This adapter does not infer a spend from a diagnostic's probability: conditional
dice decisions, rules-based free points and target/resource state are later work.
"""
from dataclasses import dataclass
from enum import Enum

from hero_resource_state import HeroResourceState
from resource_allocation import ResourceAllocation
from resource_spend_domain import ResourceSpendDomain
from hero_hunting_resource_ledger import (
    ModelResourcePlan, ModelResourceEvidence, evaluate_army_resource_plans
)


class HeroHuntingMethod(str, Enum):
    MELEE = "melee"
    SHOOTING = "shooting"
    MAGIC_CAST = "magic_cast"
    MAGIC_RESIST = "magic_resist"
    DEFENCE = "defence"


_DOMAIN = {
    HeroHuntingMethod.MELEE: ResourceSpendDomain.COMBAT,
    HeroHuntingMethod.SHOOTING: ResourceSpendDomain.COMBAT,
    HeroHuntingMethod.MAGIC_CAST: ResourceSpendDomain.MAGIC,
    HeroHuntingMethod.MAGIC_RESIST: ResourceSpendDomain.DEFENCE,
    HeroHuntingMethod.DEFENCE: ResourceSpendDomain.DEFENCE,
}


@dataclass(frozen=True)
class DeclaredMethodSpend:
    model_id: str
    method: HeroHuntingMethod
    might: int = 0
    will: int = 0
    fate: int = 0

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id must be non-blank")
        if not isinstance(self.method, HeroHuntingMethod):
            raise TypeError("method must be HeroHuntingMethod")
        for name in ("might", "will", "fate"):
            val = getattr(self, name)
            if isinstance(val, bool) or not isinstance(val, int):
                raise TypeError(f"{name} must be an integer")
            if val < 0:
                raise ValueError(f"{name} cannot be negative")


@dataclass(frozen=True)
class CrossMethodResources:
    models: tuple[ModelResourceEvidence, ...]
    declared_spends: tuple[DeclaredMethodSpend, ...]
    evidence_status: str = "explicit_cross_method_allocations_only"
    dashboard_score: None = None
    scenario_score: None = None


def reconcile_cross_method_resources(
    starting_by_model: dict[str, HeroResourceState],
    spends: tuple[DeclaredMethodSpend, ...],
) -> CrossMethodResources:
    """Fail closed for unknown actors and duplicated resource expenditure."""
    if not isinstance(starting_by_model, dict):
        raise TypeError("starting_by_model must be a dict")
    if not isinstance(spends, tuple):
        raise TypeError("spends must be a tuple")
    if not all(isinstance(s, DeclaredMethodSpend) for s in spends):
        raise TypeError("spends must contain DeclaredMethodSpend")
    for model_id, state in starting_by_model.items():
        if not isinstance(model_id, str) or not model_id.strip():
            raise ValueError("starting model_id must be non-blank")
        if not isinstance(state, HeroResourceState):
            raise TypeError("starting states must be HeroResourceState")
    unknown = {s.model_id for s in spends} - set(starting_by_model)
    if unknown:
        raise ValueError(f"Spend refers to unknown model: {sorted(unknown)[0]}")
    plans = tuple(ModelResourcePlan(
        model_id=model_id, starting=state,
        allocations=tuple(ResourceAllocation(
            domain=_DOMAIN[s.method], might=s.might, will=s.will, fate=s.fate
        ) for s in spends if s.model_id == model_id)
    ) for model_id, state in starting_by_model.items())
    return CrossMethodResources(
        models=evaluate_army_resource_plans(plans),
        declared_spends=spends,
    )
