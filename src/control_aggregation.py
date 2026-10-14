"""DEV-077S-I2-H1-C: diagnostic-only aggregation of observed Control denial.

An observation represents a specified turn and an independently verified
opportunity for one target to perform one action. The caller supplies a
snapshot of already-confirmed, not-yet-expired effects. This module neither
simulates a board nor converts probabilities into realised disruptions.

Aggregation counts each target/turn/action at most once even when multiple
spells overlap. A target/turn counts at most once as an affected model-turn.
No resources, scoring weights or durations are inferred from spell ownership.
"""
from dataclasses import dataclass

from control_effect_legality import (
    ActionLegality,
    ControlAction,
    EvidenceVerdict,
    evaluate_control_action,
)
from control_effect_state import ControlState, restrictions_for_target


@dataclass(frozen=True)
class ControlTurnObservation:
    turn: int
    target_id: str
    action: ControlAction
    state: ControlState
    opportunity: EvidenceVerdict

    def __post_init__(self) -> None:
        if type(self.turn) is not int or self.turn < 1:
            raise ValueError("turn must be a positive int")
        if not isinstance(self.target_id, str) or not self.target_id.strip():
            raise ValueError("target_id must be nonblank")
        if not isinstance(self.action, ControlAction):
            raise TypeError("action must be ControlAction")
        if not isinstance(self.state, ControlState):
            raise TypeError("state must be ControlState")
        if not isinstance(self.opportunity, EvidenceVerdict):
            raise TypeError("opportunity must be EvidenceVerdict")


@dataclass(frozen=True)
class DeniedControlOpportunity:
    turn: int
    target_id: str
    action: ControlAction
    contributing_effect_ids: tuple[str, ...]


@dataclass(frozen=True)
class ControlAggregation:
    denied_opportunities: tuple[DeniedControlOpportunity, ...]
    affected_model_turns: tuple[tuple[int, str], ...]
    unresolved_opportunities: tuple[tuple[int, str, ControlAction], ...]
    verified_non_opportunities: tuple[tuple[int, str, ControlAction], ...]
    observed_action_opportunities: int
    evidence_status: str = "observed_conditional_denial_only"
    dashboard_score: None = None
    scenario_score: None = None

    @property
    def denied_action_count(self) -> int:
        return len(self.denied_opportunities)

    @property
    def affected_model_turn_count(self) -> int:
        return len(self.affected_model_turns)


def aggregate_control_observations(
    observations: tuple[ControlTurnObservation, ...],
) -> ControlAggregation:
    """Summarise supplied, independently verified opportunities.

    Duplicate keys must agree on opportunity and derived outcome. Conflicting
    snapshots are rejected, rather than choosing the favourable one.
    Explicit expiry is the responsibility of the caller (H1-A state model).
    """
    if not isinstance(observations, tuple):
        raise TypeError("observations must be a tuple")
    records: dict[tuple[int, str, ControlAction], tuple] = {}
    for observation in observations:
        if not isinstance(observation, ControlTurnObservation):
            raise TypeError("observations must contain ControlTurnObservation")
        key = (observation.turn, observation.target_id, observation.action)
        restrictions = restrictions_for_target(observation.state, target_id=observation.target_id)
        # Other game-legality is deliberately UNKNOWN here: a verified
        # opportunity is supplied explicitly, and we only count denial.
        verdict = evaluate_control_action(
            observation.state, target_id=observation.target_id,
            action=observation.action, other_legality=EvidenceVerdict.UNKNOWN,
        )
        effective = (
            observation.opportunity,
            verdict is ActionLegality.BLOCKED_BY_CONTROL,
            tuple(sorted(set(restrictions.contributing_effect_ids))),
        )
        if key in records:
            if records[key] != effective:
                raise ValueError("conflicting evidence for target/turn/action")
            continue
        records[key] = effective

    denied: list[DeniedControlOpportunity] = []
    unresolved: list[tuple[int, str, ControlAction]] = []
    absent: list[tuple[int, str, ControlAction]] = []
    observed = 0
    affected: set[tuple[int, str]] = set()
    for (turn, target_id, action), (opportunity, blocked, sources) in sorted(
        records.items(), key=lambda item: (item[0][0], item[0][1], item[0][2].value)
    ):
        key = (turn, target_id, action)
        if opportunity is EvidenceVerdict.UNKNOWN:
            unresolved.append(key)
        elif opportunity is EvidenceVerdict.VERIFIED_FALSE:
            absent.append(key)
        else:
            observed += 1
            if blocked:
                denied.append(DeniedControlOpportunity(turn, target_id, action, sources))
                affected.add((turn, target_id))

    return ControlAggregation(
        denied_opportunities=tuple(denied),
        affected_model_turns=tuple(sorted(affected)),
        unresolved_opportunities=tuple(unresolved),
        verified_non_opportunities=tuple(absent),
        observed_action_opportunities=observed,
    )
