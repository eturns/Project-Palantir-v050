"""DEV-077-SMAUG-D4: rule-gated, conditional forced-charge evidence.

Edward Turns (Project Lead)

No pathfinding or charge-range calculation is performed. Charge legality is
supplied by a caller that has the necessary battlefield context.
"""
from dataclasses import dataclass

from forced_action_constraint import (
    ForcedActionConstraint,
    ForcedActionTarget,
    ForcedActionType,
    filter_forced_action_targets,
)

LUST_FOR_GOLD_RULE_ID = "LUST_FOR_GOLD"


@dataclass(frozen=True)
class ObjectiveCarrierChargeTarget:
    model_id: str
    enemy: bool
    carries_objective: bool
    can_charge: bool | None

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id.strip():
            raise ValueError("model_id must be a nonblank string")
        if type(self.enemy) is not bool or type(self.carries_objective) is not bool:
            raise TypeError("enemy and carries_objective must be bool")
        if self.can_charge is not None and type(self.can_charge) is not bool:
            raise TypeError("can_charge must be bool or None")


@dataclass(frozen=True)
class LustForGoldEvidence:
    rule_present: bool
    charge_required: bool | None
    permitted_target_ids: tuple[str, ...]
    eligible_carrier_ids: tuple[str, ...]
    status: str
    dashboard_score: None = None
    scenario_score: None = None


def assess_lust_for_gold(*, profile_id: str, rule_ids: frozenset[str],
                         targets: tuple[ObjectiveCarrierChargeTarget, ...] | None = None,
                         moving: bool | None = None) -> LustForGoldEvidence:
    """Determine forced-charge choice, without assuming unknown charge legality.

    If a chargeable enemy objective carrier exists, only those carriers are
    lawful charge choices. If no such carrier can be charged, this rule adds
    no constraint (other movement legality remains outside this resolver).
    """
    if not isinstance(profile_id, str):
        raise TypeError("profile_id must be a str")
    if not isinstance(rule_ids, frozenset) or not all(isinstance(x, str) for x in rule_ids):
        raise TypeError("rule_ids must be a frozenset of strings")
    if moving is not None and type(moving) is not bool:
        raise TypeError("moving must be bool or None")
    if targets is not None:
        if not isinstance(targets, tuple) or not all(isinstance(t, ObjectiveCarrierChargeTarget) for t in targets):
            raise TypeError("targets must be a tuple of ObjectiveCarrierChargeTarget")
        ids = [t.model_id for t in targets]
        if len(ids) != len(set(ids)):
            raise ValueError("target model IDs must be unique")
    rule_present = profile_id == "SMAUG" and LUST_FOR_GOLD_RULE_ID in rule_ids
    if not rule_present:
        return LustForGoldEvidence(False, False, (), (), "rule_not_present")
    if moving is False:
        return LustForGoldEvidence(True, False, (), (), "not_moving")
    if moving is None or targets is None:
        return LustForGoldEvidence(True, None, (), (), "conditional_not_evaluated")
    carriers = tuple(t for t in targets if t.enemy and t.carries_objective)
    if any(t.can_charge is None for t in carriers):
        return LustForGoldEvidence(True, None, (), tuple(t.model_id for t in carriers), "charge_legality_unknown")
    eligible = tuple(t for t in carriers if t.can_charge)
    if not eligible:
        return LustForGoldEvidence(True, False, (), (), "no_chargeable_carrier")
    constraint = ForcedActionConstraint(ForcedActionType.CHARGE, True)
    filtered = filter_forced_action_targets(
        constraint=constraint,
        targets=tuple(ForcedActionTarget(t.model_id, t in eligible) for t in targets),
        condition_met=True,
    )
    ids = tuple(t.id for t in filtered)
    return LustForGoldEvidence(True, True, ids, ids, "forced_charge")
