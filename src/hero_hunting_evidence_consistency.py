"""DEV-077S-I2-G2-E3: conservative diagnostic evidence consistency gate.

This gate does NOT aggregate probabilities, infer conditional spends, or change
capability/scenario scores. Only independently identified supported observations
can be admitted; sharing a target does not imply independent attack chances.
"""
from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

from hero_hunting_resource_adapter import (
    CrossMethodResources, HeroHuntingMethod,
)


class OutcomeType(str, Enum):
    ELIMINATION = "elimination"
    CONTROL = "control"
    RESOURCE_DEPLETION = "resource_depletion"


class EvidenceStatus(str, Enum):
    VERIFIED = "verified"
    UNSUPPORTED = "unsupported"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class MethodEvidence:
    evidence_id: str
    event_id: str
    actor_id: str
    target_id: str
    method: HeroHuntingMethod
    outcome: OutcomeType
    status: EvidenceStatus
    probability: Fraction | None
    rule_source: str | None = None

    def __post_init__(self) -> None:
        for name in ("evidence_id", "event_id", "actor_id", "target_id"):
            val = getattr(self, name)
            if not isinstance(val, str) or not val.strip():
                raise ValueError(f"{name} must be a non-blank string")
        if not isinstance(self.method, HeroHuntingMethod):
            raise TypeError("method must be HeroHuntingMethod")
        if not isinstance(self.outcome, OutcomeType):
            raise TypeError("outcome must be OutcomeType")
        if not isinstance(self.status, EvidenceStatus):
            raise TypeError("status must be EvidenceStatus")
        if self.probability is not None:
            if isinstance(self.probability, bool) or not isinstance(self.probability, Fraction):
                raise TypeError("probability must be Fraction or None")
            if not 0 <= self.probability <= 1:
                raise ValueError("probability must be between zero and one")
        if self.status is EvidenceStatus.VERIFIED:
            if self.probability is None:
                raise ValueError("verified evidence requires a probability")
            if not isinstance(self.rule_source, str) or not self.rule_source.strip():
                raise ValueError("verified evidence requires rule_source")
        elif self.probability is not None:
            raise ValueError("unsupported or unresolved evidence cannot declare probability")


@dataclass(frozen=True)
class ConsistencyEvidence:
    observations: tuple[MethodEvidence, ...]
    resource_evidence: CrossMethodResources
    verified_count: int
    unresolved_count: int
    evidence_status: str = "diagnostic_only_not_aggregated"
    elimination_probability: None = None
    dashboard_score: None = None
    scenario_score: None = None


def check_hero_hunting_evidence(
    observations: tuple[MethodEvidence, ...],
    resource_evidence: CrossMethodResources,
) -> ConsistencyEvidence:
    """Validate declared observations and already-reconciled resource ledger.

    Different events against the same target are allowed but NOT combined.
    One event may have different outcomes (e.g. control and elimination) but
    its same outcome cannot be included twice under separate evidence IDs.
    """
    if not isinstance(observations, tuple) or not all(
        isinstance(x, MethodEvidence) for x in observations
    ):
        raise TypeError("observations must be a tuple of MethodEvidence")
    if not isinstance(resource_evidence, CrossMethodResources):
        raise TypeError("resource_evidence must be CrossMethodResources")
    actors = {x.model_id for x in resource_evidence.models}
    evidence_ids = set()
    outcome_events = set()
    for item in observations:
        if item.actor_id not in actors:
            raise ValueError(f"Unknown acting model: {item.actor_id}")
        if item.evidence_id in evidence_ids:
            raise ValueError(f"Duplicate evidence_id: {item.evidence_id}")
        evidence_ids.add(item.evidence_id)
        event_key = (item.event_id, item.actor_id, item.target_id, item.outcome)
        if event_key in outcome_events:
            raise ValueError("Duplicate event/outcome evidence")
        outcome_events.add(event_key)
    return ConsistencyEvidence(
        observations=observations,
        resource_evidence=resource_evidence,
        verified_count=sum(x.status is EvidenceStatus.VERIFIED for x in observations),
        unresolved_count=sum(x.status is not EvidenceStatus.VERIFIED for x in observations),
    )
