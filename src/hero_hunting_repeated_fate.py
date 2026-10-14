"""DEV-077S-I2-G3-B5A: repeated Fate rolls against one Wound.

2024 MESBG Rules Manual p.87: each Fate attempt costs a point, saves on 4+,
and failed attempts may be repeated one at a time. This model uses a declared
maximum number of rolls per Wound, never an inferred optimal policy.

Might interventions and Will-as-Fate are intentionally NOT included here.
"""
from dataclasses import dataclass
from fractions import Fraction
from hero_hunting_target_survival import (
    TargetSurvivalState, VerifiedTargetEvent, evaluate_target_survival,
)

HALF = Fraction(1, 2)


@dataclass(frozen=True)
class FateAttemptPolicy:
    max_attempts_per_wound: int

    def __post_init__(self):
        n = self.max_attempts_per_wound
        if isinstance(n, bool) or not isinstance(n, int):
            raise TypeError("max_attempts_per_wound must be an integer")
        if n < 0:
            raise ValueError("max_attempts_per_wound cannot be negative")


def repeated_fate_transition(
    state: TargetSurvivalState,
    conditional_wound_probability: Fraction,
    policy: FateAttemptPolicy,
) -> dict[TargetSurvivalState, Fraction]:
    """Exact mutually-exclusive outcomes for one Wound opportunity.

    The player stops after the first successful Fate roll, or when the
    declared cap / available Fate is exhausted. No resource reset occurs.
    """
    if not isinstance(state, TargetSurvivalState) or state.wounds <= 0:
        raise ValueError("state must be a living TargetSurvivalState")
    if not isinstance(policy, FateAttemptPolicy):
        raise TypeError("policy must be FateAttemptPolicy")
    p = conditional_wound_probability
    if isinstance(p, bool) or not isinstance(p, Fraction):
        raise TypeError("conditional_wound_probability must be Fraction")
    if not 0 <= p <= 1:
        raise ValueError("conditional_wound_probability out of range")
    outcomes = {}
    def add(s, chance):
        if chance:
            outcomes[s] = outcomes.get(s, Fraction(0)) + chance
    add(state, 1-p)
    attempts = min(state.fate, policy.max_attempts_per_wound)
    fail_all = p
    for used in range(1, attempts+1):
        add(TargetSurvivalState(state.wounds, state.fate-used, state.will), fail_all * HALF)
        fail_all *= HALF
    add(TargetSurvivalState(state.wounds-1, state.fate-attempts, state.will), fail_all)
    return outcomes


@dataclass(frozen=True)
class RepeatedFateWoundEvent:
    event_id: str
    target_id: str
    rule_source: str
    conditional_wound_probability: Fraction
    policy: FateAttemptPolicy

    def __post_init__(self):
        for name in ("event_id", "target_id", "rule_source"):
            x=getattr(self,name)
            if not isinstance(x,str) or not x.strip():
                raise ValueError(f"{name} must be documented")
        if not isinstance(self.policy,FateAttemptPolicy):
            raise TypeError("policy must be FateAttemptPolicy")


def evaluate_repeated_fate_events(target_id, initial, events):
    if not isinstance(events,tuple) or not all(isinstance(e,RepeatedFateWoundEvent) for e in events):
        raise TypeError("events must be a tuple of RepeatedFateWoundEvent")
    converted=tuple(VerifiedTargetEvent(
        event_id=e.event_id,target_id=e.target_id,rule_source=e.rule_source,
        transition=lambda state, evt=e: repeated_fate_transition(
            state,evt.conditional_wound_probability,evt.policy)
    ) for e in events)
    return evaluate_target_survival(target_id,initial,converted)
