"""DEV-077S-I2-G3-C2: exclusive attacker opportunities and finite budgets.

A slot is a caller-verified opportunity, not a claim that all models can
attack once per turn. Distinct slots may be supplied for rules-verified
multiple attacks/casts. Does not infer turn timing, LoS or joint odds.
"""
from dataclasses import dataclass

from hero_resource_state import HeroResourceState
from hero_hunting_army_collection import ArmyHeroHuntingCollection
from hero_hunting_evidence_consistency import EvidenceStatus
from hero_hunting_resource_adapter import (
    DeclaredMethodSpend, CrossMethodResources,
    reconcile_cross_method_resources,
)


@dataclass(frozen=True)
class AllocatedAttack:
    evidence_id: str
    opportunity_id: str
    spend: DeclaredMethodSpend

    def __post_init__(self):
        for key in ('evidence_id', 'opportunity_id'):
            value = getattr(self, key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f'{key} must be nonblank')
        if not isinstance(self.spend, DeclaredMethodSpend):
            raise TypeError('spend must be DeclaredMethodSpend')


@dataclass(frozen=True)
class ArmyAttackAllocation:
    selected_evidence_ids: tuple[str, ...]
    selected_target_ids: tuple[str, ...]
    selected_event_ids: tuple[str, ...]
    remaining_resources: CrossMethodResources
    evidence_status: str = 'explicit_exclusive_attack_plan_no_joint_probability'
    any_target_elimination_probability: None = None
    dashboard_score: None = None
    scenario_score: None = None


def validate_army_attack_allocation(
    collection: ArmyHeroHuntingCollection,
    choices: tuple[AllocatedAttack, ...],
    starting_resources: dict[str, HeroResourceState],
    prior_spends: tuple[DeclaredMethodSpend, ...] = (),
) -> ArmyAttackAllocation:
    """Reject duplicate opportunity use, unverifiable events and overspending.

    All spending is for explicit selected events only; no inference that an
    unselected alternative has been executed. A single opportunity may
    represent a cast, a shot, or a combat participation, as verified upstream.
    """
    if not isinstance(collection, ArmyHeroHuntingCollection):
        raise TypeError('collection must be ArmyHeroHuntingCollection')
    if not isinstance(choices, tuple) or any(not isinstance(x, AllocatedAttack) for x in choices):
        raise TypeError('choices must be tuple of AllocatedAttack')
    if not isinstance(prior_spends, tuple) or any(not isinstance(x, DeclaredMethodSpend) for x in prior_spends):
        raise TypeError('prior_spends must be tuple of DeclaredMethodSpend')
    observations = {x.evidence_id: x for x in collection.observations}
    seen_evidence, seen_opportunities, seen_events = set(), set(), set()
    selected = []
    for choice in choices:
        if choice.evidence_id in seen_evidence:
            raise ValueError('Duplicate selected evidence')
        seen_evidence.add(choice.evidence_id)
        obs = observations.get(choice.evidence_id)
        if obs is None:
            raise ValueError('Unknown selected evidence')
        if obs.status is not EvidenceStatus.VERIFIED:
            raise ValueError('Selected evidence must be verified')
        if obs.actor_id != choice.spend.model_id or obs.method != choice.spend.method:
            raise ValueError('Selected spend must match observation actor and method')
        slot = (obs.actor_id, choice.opportunity_id)
        if slot in seen_opportunities:
            raise ValueError('Attacker opportunity allocated twice')
        seen_opportunities.add(slot)
        event = (obs.actor_id, obs.event_id)
        if event in seen_events:
            raise ValueError('One event allocated to multiple outcomes or targets')
        seen_events.add(event)
        selected.append(obs)
    # Collection must correspond to the same starting resource set, after any
    # explicit previously recorded spending. Prevent forged actor identities.
    ledger = reconcile_cross_method_resources(
        starting_resources, prior_spends + tuple(c.spend for c in choices)
    )
    if {m.model_id for m in ledger.models} != {m.model_id for m in collection.resource_evidence.models}:
        raise ValueError('Resource model set must match collected evidence')
    return ArmyAttackAllocation(
        selected_evidence_ids=tuple(x.evidence_id for x in selected),
        selected_target_ids=tuple(sorted({x.target_id for x in selected})),
        selected_event_ids=tuple(x.event_id for x in selected),
        remaining_resources=ledger,
    )
