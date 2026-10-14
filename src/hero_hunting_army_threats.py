"""DEV-077S-I2-G3-C1: per-target army threat results, no joint probability.

A target result is accepted only when its ordered event IDs correspond to
verified elimination observations. Other effect types remain distinct. The
aggregator does not infer dependencies, attacker availability, or scoring.
"""
from dataclasses import dataclass
from fractions import Fraction

from hero_hunting_army_collection import ArmyHeroHuntingCollection
from hero_hunting_evidence_consistency import EvidenceStatus
from hero_hunting_unified_defence import UnifiedDefenceEvidence


@dataclass(frozen=True)
class ArmyTargetThreat:
    target_id: str
    elimination_probability: Fraction | None
    survival_probability: Fraction | None
    event_ids: tuple[str, ...]
    verified_events: int
    unresolved_events: int
    status: str


@dataclass(frozen=True)
class ArmyThreatEvidence:
    targets: tuple[ArmyTargetThreat, ...]
    evidence_status: str = 'target_threats_only_no_joint_probability'
    any_target_elimination_probability: None = None
    dashboard_score: None = None
    scenario_score: None = None


def aggregate_army_target_threats(
    collection: ArmyHeroHuntingCollection,
    results: tuple[UnifiedDefenceEvidence, ...],
) -> ArmyThreatEvidence:
    if not isinstance(collection, ArmyHeroHuntingCollection):
        raise TypeError('collection must be ArmyHeroHuntingCollection')
    if not isinstance(results, tuple) or any(
        not isinstance(r, UnifiedDefenceEvidence) for r in results
    ):
        raise TypeError('results must contain UnifiedDefenceEvidence')
    lookup = {}
    for result in results:
        if result.target_id in lookup:
            raise ValueError('Duplicate target result')
        lookup[result.target_id] = result
    known = {target.target_id for target in collection.targets}
    if set(lookup) - known:
        raise ValueError('Result references unknown target')

    threats = []
    for target in collection.targets:
        verified = tuple(
            obs for obs in target.elimination_observations
            if obs.status is EvidenceStatus.VERIFIED
        )
        unresolved = len(target.observations) - sum(
            obs.status is EvidenceStatus.VERIFIED for obs in target.observations
        )
        result = lookup.get(target.target_id)
        if result is None:
            threats.append(ArmyTargetThreat(
                target.target_id, None, None, (), len(verified), unresolved,
                'not_evaluated',
            ))
            continue
        expected_ids = tuple(obs.event_id for obs in verified)
        if len(expected_ids) != len(set(expected_ids)):
            raise ValueError('Ambiguous repeated event_id in target evidence')
        if set(result.event_ids) != set(expected_ids) or len(result.event_ids) != len(expected_ids):
            raise ValueError('Evaluated events do not match verified elimination evidence')
        if not isinstance(result.elimination_probability, Fraction) or not (
            Fraction(0) <= result.elimination_probability <= Fraction(1)
        ):
            raise ValueError('Invalid elimination probability')
        if result.survival_probability != 1 - result.elimination_probability:
            raise ValueError('Survival probability inconsistent with elimination')
        threats.append(ArmyTargetThreat(
            target.target_id, result.elimination_probability,
            result.survival_probability, result.event_ids,
            len(verified), unresolved,
            'verified_conditional' if unresolved == 0 else 'partial_unresolved',
        ))
    return ArmyThreatEvidence(tuple(threats))
