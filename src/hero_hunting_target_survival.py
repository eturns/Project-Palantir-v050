"""DEV-077S-I2-G3-B1: exact, declared conditional target-state transitions.

This engine never treats standalone MethodEvidence probabilities as independent.
A caller must supply a verified transition distribution conditional on the
current state for each event; probabilities are exact Fractions. Wounds/Fate/Will
are shared between events. No dashboard or scenario score is produced.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable


@dataclass(frozen=True, order=True)
class TargetSurvivalState:
    wounds: int
    fate: int = 0
    will: int = 0

    def __post_init__(self):
        for field in ('wounds', 'fate', 'will'):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f'{field} must be an integer')
            if value < 0:
                raise ValueError(f'{field} cannot be negative')


@dataclass(frozen=True)
class VerifiedTargetEvent:
    event_id: str
    target_id: str
    rule_source: str
    transition: Callable[[TargetSurvivalState], dict[TargetSurvivalState, Fraction]]

    def __post_init__(self):
        if any(not isinstance(getattr(self, x), str) or not getattr(self, x).strip()
               for x in ('event_id', 'target_id', 'rule_source')):
            raise ValueError('event_id, target_id and rule_source must be documented')
        if not callable(self.transition):
            raise TypeError('transition must be callable')


@dataclass(frozen=True)
class TargetSurvivalEvidence:
    target_id: str
    event_ids: tuple[str, ...]
    surviving_states: dict[TargetSurvivalState, Fraction]
    elimination_probability: Fraction
    survival_probability: Fraction
    evidence_status: str = 'conditional_transitions_verified_by_caller'
    dashboard_score: None = None
    scenario_score: None = None


def evaluate_target_survival(
    target_id: str,
    initial: TargetSurvivalState,
    events: tuple[VerifiedTargetEvent, ...],
) -> TargetSurvivalEvidence:
    """Propagate exact state probabilities in declared chronological order.

    State wounds=0 is absorbing: subsequent events cannot resurrect the hero.
    An event's transition must conserve probability for each reachable state,
    cannot increase Wounds/Fate/Will, and must not change a dead target.
    More complex recovery/buffs require a separate verified contract.
    """
    if not isinstance(target_id, str) or not target_id.strip():
        raise ValueError('target_id must be non-blank')
    if not isinstance(initial, TargetSurvivalState) or initial.wounds == 0:
        raise ValueError('initial must describe a living TargetSurvivalState')
    if not isinstance(events, tuple) or not all(isinstance(e, VerifiedTargetEvent) for e in events):
        raise TypeError('events must be a tuple of VerifiedTargetEvent')
    ids = [e.event_id for e in events]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate event_id')
    if any(e.target_id != target_id for e in events):
        raise ValueError('Event target mismatch')

    states = {initial: Fraction(1)}
    for event in events:
        next_states = {}
        for state, chance in states.items():
            if chance == 0:
                continue
            if state.wounds == 0:
                next_states[state] = next_states.get(state, Fraction(0)) + chance
                continue
            transitions = event.transition(state)
            if not isinstance(transitions, dict) or not transitions:
                raise ValueError('Missing conditional transition distribution')
            total = Fraction(0)
            for after, probability in transitions.items():
                if not isinstance(after, TargetSurvivalState):
                    raise TypeError('Transition states must be TargetSurvivalState')
                if isinstance(probability, bool) or not isinstance(probability, Fraction):
                    raise TypeError('Transition probabilities must be Fractions')
                if not 0 <= probability <= 1:
                    raise ValueError('Transition probability out of range')
                if (after.wounds > state.wounds or after.fate > state.fate
                        or after.will > state.will):
                    raise ValueError('Unverified resource or wound recovery')
                total += probability
                if probability == 0:
                    continue
                next_states[after] = next_states.get(after, Fraction(0)) + chance * probability
            if total != 1:
                raise ValueError('Conditional transition probabilities must total one')
        states = next_states
    dead = sum((p for state, p in states.items() if state.wounds == 0), Fraction(0))
    return TargetSurvivalEvidence(
        target_id=target_id, event_ids=tuple(ids), surviving_states=states,
        elimination_probability=dead, survival_probability=1-dead,
    )
