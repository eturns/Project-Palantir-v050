"""DEV-077S-I2-G3-A: army-level Hero Hunting evidence collection.

Collects per-model observations and keeps target-level evidence separate.
No probability aggregation, inferred independence, scoring or resource spends.
"""
from dataclasses import dataclass

from hero_hunting_evidence_consistency import (
    ConsistencyEvidence, EvidenceStatus, MethodEvidence, OutcomeType,
    check_hero_hunting_evidence,
)
from hero_hunting_resource_adapter import (
    CrossMethodResources, HeroHuntingMethod,
)


@dataclass(frozen=True)
class TargetEvidence:
    target_id: str
    observations: tuple[MethodEvidence, ...]
    verified_count: int
    unresolved_count: int
    elimination_observations: tuple[MethodEvidence, ...]
    control_observations: tuple[MethodEvidence, ...]
    resource_observations: tuple[MethodEvidence, ...]
    elimination_probability: None = None


@dataclass(frozen=True)
class ArmyHeroHuntingCollection:
    observations: tuple[MethodEvidence, ...]
    targets: tuple[TargetEvidence, ...]
    actors: tuple[str, ...]
    resource_evidence: CrossMethodResources
    verified_count: int
    unresolved_count: int
    evidence_status: str = "collected_not_aggregated"
    elimination_probability: None = None
    dashboard_score: None = None
    scenario_score: None = None


def collect_army_hero_hunting_evidence(
    batches: tuple[tuple[MethodEvidence, ...], ...],
    resource_evidence: CrossMethodResources,
) -> ArmyHeroHuntingCollection:
    """Combine evidence batches, rejecting duplicate observations globally.

    Each batch may originate from melee, shooting or magic diagnostics;
    individual records retain their method and event identity. One actor's
    events can target several heroes; events against one hero stay distinct.
    """
    if not isinstance(batches, tuple):
        raise TypeError("batches must be a tuple")
    if not all(isinstance(batch, tuple) for batch in batches):
        raise TypeError("each batch must be a tuple")
    if not all(isinstance(item, MethodEvidence)
               for batch in batches for item in batch):
        raise TypeError("batches must contain MethodEvidence")
    observations = tuple(item for batch in batches for item in batch)
    checked: ConsistencyEvidence = check_hero_hunting_evidence(
        observations=observations,
        resource_evidence=resource_evidence,
    )
    target_ids = tuple(sorted({item.target_id for item in observations}))
    targets = []
    for target_id in target_ids:
        items = tuple(item for item in observations if item.target_id == target_id)
        targets.append(TargetEvidence(
            target_id=target_id,
            observations=items,
            verified_count=sum(item.status is EvidenceStatus.VERIFIED for item in items),
            unresolved_count=sum(item.status is not EvidenceStatus.VERIFIED for item in items),
            elimination_observations=tuple(
                item for item in items if item.outcome is OutcomeType.ELIMINATION
            ),
            control_observations=tuple(
                item for item in items if item.outcome is OutcomeType.CONTROL
            ),
            resource_observations=tuple(
                item for item in items if item.outcome is OutcomeType.RESOURCE_DEPLETION
            ),
        ))
    return ArmyHeroHuntingCollection(
        observations=checked.observations,
        targets=tuple(targets),
        actors=tuple(sorted({item.actor_id for item in observations})),
        resource_evidence=checked.resource_evidence,
        verified_count=checked.verified_count,
        unresolved_count=checked.unresolved_count,
    )
