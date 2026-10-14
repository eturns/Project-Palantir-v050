"""DEV-077S-I2-G3-C3: explainable *conditional* army Hero Hunting plans.

No joint target probability, automatic plan selection, or calibrated score.
C1 result probabilities apply only if their event set matches a feasible C2
allocation for that target exactly. Unselected alternatives stay unassessed.
"""
from dataclasses import dataclass
from fractions import Fraction

from hero_hunting_army_collection import ArmyHeroHuntingCollection
from hero_hunting_army_threats import ArmyThreatEvidence
from hero_hunting_attacker_allocation import ArmyAttackAllocation
from hero_hunting_evidence_consistency import OutcomeType


@dataclass(frozen=True)
class ExplainedTarget:
    target_id: str
    selected_event_ids: tuple[str, ...]
    attackers: tuple[str, ...]
    methods: tuple[str, ...]
    elimination_probability: Fraction | None
    status: str
    unresolved_events: int


@dataclass(frozen=True)
class ExplainedArmyCapability:
    targets: tuple[ExplainedTarget, ...]
    selected_evidence_ids: tuple[str, ...]
    selected_attack_count: int
    remaining_resources: tuple[tuple[str, int, int, int], ...]
    evidence_status: str = 'declared_plan_conditional_not_calibrated'
    any_target_elimination_probability: None = None
    dashboard_score: None = None
    scenario_score: None = None


def explain_army_hero_hunting_plan(
    collection: ArmyHeroHuntingCollection,
    allocation: ArmyAttackAllocation,
    threats: ArmyThreatEvidence,
) -> ExplainedArmyCapability:
    """Explain one validated declared plan, never sum marginal probabilities.

    A C1 threat represents all verified elimination events for its target.
    If only some are selected, that probability cannot be reused for this plan.
    """
    if not isinstance(collection, ArmyHeroHuntingCollection):
        raise TypeError('collection must be ArmyHeroHuntingCollection')
    if not isinstance(allocation, ArmyAttackAllocation):
        raise TypeError('allocation must be ArmyAttackAllocation')
    if not isinstance(threats, ArmyThreatEvidence):
        raise TypeError('threats must be ArmyThreatEvidence')
    observations = {o.evidence_id: o for o in collection.observations}
    if len(observations) != len(collection.observations):
        raise ValueError('Duplicate collection evidence')
    ids = allocation.selected_evidence_ids
    if len(set(ids)) != len(ids) or any(eid not in observations for eid in ids):
        raise ValueError('Selection does not match collection evidence')
    selected = tuple(observations[eid] for eid in ids)
    if (tuple(sorted({o.target_id for o in selected})) != allocation.selected_target_ids
            or tuple(o.event_id for o in selected) != allocation.selected_event_ids):
        raise ValueError('Selection identity does not match allocation')
    if {x.model_id for x in allocation.remaining_resources.models} != {
        x.model_id for x in collection.resource_evidence.models
    }:
        raise ValueError('Allocation resource models do not match collection')
    threat_lookup = {t.target_id: t for t in threats.targets}
    if len(threat_lookup) != len(threats.targets):
        raise ValueError('Duplicate threat targets')
    if set(threat_lookup) != {t.target_id for t in collection.targets}:
        raise ValueError('Threat targets do not match collection')
    rows=[]
    for target in collection.targets:
        target_obs=tuple(o for o in selected if o.target_id == target.target_id)
        elim=tuple(o for o in target_obs if o.outcome is OutcomeType.ELIMINATION)
        threat=threat_lookup[target.target_id]
        selected_ids=tuple(o.event_id for o in elim)
        # A probability from the C1 evaluator is valid only for the precise
        # set of elimination events being executed by this C2 plan.
        exact=(len(selected_ids)==len(threat.event_ids)
               and set(selected_ids)==set(threat.event_ids))
        complete=(threat.status == 'verified_conditional'
                  and threat.unresolved_events == 0)
        if not target_obs:
            probability=None
            status='not_allocated'
        elif not elim:
            probability=None
            status='non_elimination_only'
        elif not exact:
            probability=None
            status='selected_subset_not_evaluated'
        elif not complete or threat.elimination_probability is None:
            probability=None
            status='unresolved_target_evidence'
        else:
            probability=threat.elimination_probability
            status='verified_conditional_plan'
        rows.append(ExplainedTarget(
            target_id=target.target_id,
            selected_event_ids=tuple(o.event_id for o in target_obs),
            attackers=tuple(sorted({o.actor_id for o in target_obs})),
            methods=tuple(sorted({o.method.value for o in target_obs})),
            elimination_probability=probability,
            status=status,
            unresolved_events=threat.unresolved_events,
        ))
    resources=tuple(sorted((m.model_id,m.remaining.remaining_might,
             m.remaining.remaining_will,m.remaining.remaining_fate)
             for m in allocation.remaining_resources.models))
    return ExplainedArmyCapability(
        targets=tuple(rows), selected_evidence_ids=ids,
        selected_attack_count=len(ids), remaining_resources=resources,
    )
