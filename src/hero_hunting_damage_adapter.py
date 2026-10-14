"""DEV-077S-I2-G3-B2: verified damage-event bridge to G3-B1.

Caller supplies state-conditional distributions; a MethodEvidence probability
is NEVER reinterpreted as a wound probability. This is a narrow integration
contract, not automated melee/shooting/magic outcome extraction.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

from hero_hunting_evidence_consistency import EvidenceStatus, MethodEvidence, OutcomeType
from hero_hunting_resource_adapter import HeroHuntingMethod
from hero_hunting_target_survival import (
    TargetSurvivalState, VerifiedTargetEvent, TargetSurvivalEvidence,
    evaluate_target_survival,
)

_DAMAGE_METHODS = frozenset((
    HeroHuntingMethod.MELEE,
    HeroHuntingMethod.SHOOTING,
    HeroHuntingMethod.MAGIC_CAST,
))


@dataclass(frozen=True)
class VerifiedDamageEvent:
    """One already-verified attack with state-conditional damage outcomes.

    The resolver describes probabilities for target states *after* all wound
    prevention, Fate/Will use and damage. Shared resources for attacking
    models must separately pass the E2 resource ledger.
    """
    observation: MethodEvidence
    conditional_outcomes: Callable[
        [TargetSurvivalState], dict[TargetSurvivalState, Fraction]
    ]
    transition_rule_source: str

    def __post_init__(self):
        if not isinstance(self.observation, MethodEvidence):
            raise TypeError("observation must be MethodEvidence")
        if self.observation.status is not EvidenceStatus.VERIFIED:
            raise ValueError("damage event requires verified evidence")
        if self.observation.method not in _DAMAGE_METHODS:
            raise ValueError("unsupported damage method")
        if self.observation.outcome is not OutcomeType.ELIMINATION:
            raise ValueError("damage event requires elimination outcome")
        if not callable(self.conditional_outcomes):
            raise TypeError("conditional_outcomes must be callable")
        if (not isinstance(self.transition_rule_source, str)
                or not self.transition_rule_source.strip()):
            raise ValueError("transition_rule_source must be documented")


def evaluate_damage_event_sequence(
    target_id: str,
    initial: TargetSurvivalState,
    events: tuple[VerifiedDamageEvent, ...],
) -> TargetSurvivalEvidence:
    """Resolve an ordered target sequence without asserting independence."""
    if not isinstance(events, tuple) or not all(
        isinstance(event, VerifiedDamageEvent) for event in events
    ):
        raise TypeError("events must be a tuple of VerifiedDamageEvent")
    return evaluate_target_survival(
        target_id=target_id,
        initial=initial,
        events=tuple(
            VerifiedTargetEvent(
                event_id=event.observation.event_id,
                target_id=event.observation.target_id,
                rule_source=event.transition_rule_source,
                transition=event.conditional_outcomes,
            )
            for event in events
        ),
    )


def verified_unprevented_single_wound(
    observation: MethodEvidence,
    *,
    conditional_wound_probability: Callable[[TargetSurvivalState], Fraction],
    no_prevention_verified: bool,
    transition_rule_source: str,
) -> VerifiedDamageEvent:
    """Helper for ONE wound where no defensive prevention is possible.

    The callback MUST provide state-conditional wound probability from an
    established mechanical model. Does not derive it from the observation.
    """
    if no_prevention_verified is not True:
        raise ValueError("absence of wound prevention must be verified")
    if not callable(conditional_wound_probability):
        raise TypeError("conditional_wound_probability must be callable")

    def transitions(state: TargetSurvivalState) -> dict[TargetSurvivalState, Fraction]:
        chance = conditional_wound_probability(state)
        if isinstance(chance, bool) or not isinstance(chance, Fraction):
            raise TypeError("conditional wound probability must be Fraction")
        if not 0 <= chance <= 1:
            raise ValueError("conditional wound probability out of range")
        wounded = TargetSurvivalState(state.wounds - 1, state.fate, state.will)
        unchanged = state
        distribution: dict[TargetSurvivalState, Fraction] = {}
        if chance:
            distribution[wounded] = chance
        if chance < 1:
            distribution[unchanged] = 1 - chance
        return distribution

    return VerifiedDamageEvent(
        observation=observation,
        conditional_outcomes=transitions,
        transition_rule_source=transition_rule_source,
    )
