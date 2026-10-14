"""DEV-077S-I2-G3-B6: Might-aware target survival and shared resource bridge.

Uses existing B5B exact DefenceResources transitions. The earlier B1 engine
cannot represent Might: do not silently coerce its states to/from this model.
Explicit E2 model budgets are checked against the initial defensive state.
No scoring changes, no attacker spending or strategy optimisation.
"""
from dataclasses import dataclass
from collections import defaultdict
from fractions import Fraction
from typing import Callable

from hero_hunting_might_will_defence import (
    DefenceResources, DefencePolicy, defended_wound_distribution,
)
from hero_hunting_resource_adapter import CrossMethodResources


@dataclass(frozen=True)
class UnifiedDefenceEvent:
    event_id: str
    target_id: str
    rule_source: str
    conditional_wound_probability: Callable[[DefenceResources], Fraction]
    policy: DefencePolicy

    def __post_init__(self):
        for field in ("event_id", "target_id", "rule_source"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be documented")
        if not callable(self.conditional_wound_probability):
            raise TypeError("conditional_wound_probability must be callable")
        if not isinstance(self.policy, DefencePolicy):
            raise TypeError("policy must be DefencePolicy")


@dataclass(frozen=True)
class UnifiedDefenceEvidence:
    target_id: str
    event_ids: tuple[str, ...]
    final_states: dict[DefenceResources, Fraction]
    elimination_probability: Fraction
    survival_probability: Fraction
    evidence_status: str = "verified_conditional_defence_plan"
    dashboard_score: None = None
    scenario_score: None = None


def evaluate_unified_defence(
    target_id: str,
    initial: DefenceResources,
    events: tuple[UnifiedDefenceEvent, ...],
    resource_evidence: CrossMethodResources,
) -> UnifiedDefenceEvidence:
    if not isinstance(target_id, str) or not target_id.strip():
        raise ValueError("target_id must be non-blank")
    if not isinstance(initial, DefenceResources) or initial.wounds == 0:
        raise ValueError("initial must be a living DefenceResources")
    if not isinstance(events, tuple) or any(not isinstance(e, UnifiedDefenceEvent) for e in events):
        raise TypeError("events must be a tuple of UnifiedDefenceEvent")
    if not isinstance(resource_evidence, CrossMethodResources):
        raise TypeError("resource_evidence must be CrossMethodResources")
    ids = tuple(e.event_id for e in events)
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate event_id")
    if any(e.target_id != target_id for e in events):
        raise ValueError("Event target mismatch")
    actors = [m for m in resource_evidence.models if m.model_id == target_id]
    if len(actors) != 1:
        raise ValueError("defender requires exactly one E2 resource budget")
    available = actors[0].remaining
    if (initial.might, initial.will, initial.fate) != (
        available.remaining_might, available.remaining_will, available.remaining_fate
    ):
        raise ValueError("initial defensive resources must match E2 remaining budget")

    states = {initial: Fraction(1)}
    for event in events:
        updated = defaultdict(Fraction)
        for state, mass in states.items():
            if state.wounds == 0:
                updated[state] += mass
                continue
            wound_p = event.conditional_wound_probability(state)
            branches = defended_wound_distribution(state, wound_p, event.policy)
            if not branches or sum(branches.values(), Fraction(0)) != 1:
                raise ValueError("conditional transitions must total one")
            for after, p in branches.items():
                if (after.wounds > state.wounds or after.fate > state.fate
                        or after.will > state.will or after.might > state.might):
                    raise ValueError("Unverified wound/resource recovery")
                updated[after] += mass * p
        states = {state: prob for state, prob in updated.items() if prob}
    eliminated = sum((prob for state, prob in states.items() if state.wounds == 0),Fraction(0))
    return UnifiedDefenceEvidence(
        target_id=target_id,event_ids=ids,final_states=states,
        elimination_probability=eliminated,survival_probability=1-eliminated
    )
