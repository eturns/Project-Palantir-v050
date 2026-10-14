"""DEV-077S-I2-G3-B4 — stateful defence for verified single-wound events.

2024 Rules Manual p.87 (PDF p.88): a Fate attempt costs one Fate and saves
a Wound on 4+. Automatic repeated Fate attempts are NOT assumed.
Will-based protection requires an explicitly supplied verified special rule.
No Might modification, multi-wound attack or score changes.
"""
from dataclasses import dataclass
from fractions import Fraction
from typing import Callable

from hero_hunting_target_survival import (
    TargetSurvivalState, VerifiedTargetEvent, TargetSurvivalEvidence,
    evaluate_target_survival,
)

FATE_SAVE_PROBABILITY = Fraction(1, 2)


@dataclass(frozen=True)
class VerifiedDefencePlan:
    """Declare decisions, never infer optional Fate/Will spending."""
    spend_one_fate_if_wounded: bool = False
    spend_one_will_if_wounded: bool = False
    will_save_probability: Fraction | None = None
    will_rule_source: str | None = None

    def __post_init__(self):
        for name in ("spend_one_fate_if_wounded", "spend_one_will_if_wounded"):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be bool")
        if self.spend_one_will_if_wounded:
            if (not isinstance(self.will_save_probability, Fraction)
                    or not 0 <= self.will_save_probability <= 1):
                raise ValueError("Will defence requires verified save probability")
            if not self.will_rule_source or not self.will_rule_source.strip():
                raise ValueError("Will defence requires verified rule source")
        elif self.will_save_probability is not None or self.will_rule_source is not None:
            raise ValueError("Unspent Will defence must not carry unsupported rule data")
        if self.spend_one_fate_if_wounded and self.spend_one_will_if_wounded:
            raise ValueError("Cannot stack Fate and Will on a wound without a verified ordering contract")


def single_wound_defence_transition(
    state: TargetSurvivalState,
    wound_probability: Fraction,
    plan: VerifiedDefencePlan,
) -> dict[TargetSurvivalState, Fraction]:
    """A conditional, single unprevented Wound opportunity and one defence roll.

    The declared one-Fate policy is attempted if Fate remains; with none
    remaining the wound is taken. Both a successful and a failed roll spend Fate.
    """
    if not isinstance(state, TargetSurvivalState) or state.wounds == 0:
        raise ValueError("state must be a living TargetSurvivalState")
    if isinstance(wound_probability, bool) or not isinstance(wound_probability, Fraction):
        raise TypeError("wound_probability must be Fraction")
    if not 0 <= wound_probability <= 1:
        raise ValueError("wound_probability out of range")
    if not isinstance(plan, VerifiedDefencePlan):
        raise TypeError("plan must be VerifiedDefencePlan")

    result: dict[TargetSurvivalState, Fraction] = {}
    def add(s: TargetSurvivalState, p: Fraction):
        if p:
            result[s] = result.get(s, Fraction(0)) + p

    add(state, 1 - wound_probability)
    if plan.spend_one_fate_if_wounded and state.fate:
        add(TargetSurvivalState(state.wounds, state.fate - 1, state.will),
            wound_probability * FATE_SAVE_PROBABILITY)
        add(TargetSurvivalState(state.wounds - 1, state.fate - 1, state.will),
            wound_probability * (1-FATE_SAVE_PROBABILITY))
    elif plan.spend_one_will_if_wounded:
        if state.will == 0:
            # No Will to spend: defender cannot use optional protection.
            add(TargetSurvivalState(state.wounds - 1, state.fate, state.will),
                wound_probability)
        else:
            saved = plan.will_save_probability
            add(TargetSurvivalState(state.wounds, state.fate, state.will - 1),
                wound_probability * saved)
            add(TargetSurvivalState(state.wounds - 1, state.fate, state.will - 1),
                wound_probability * (1 - saved))
    else:
        add(TargetSurvivalState(state.wounds - 1, state.fate, state.will),
            wound_probability)
    return result


@dataclass(frozen=True)
class StatefulDefendedWound:
    event_id: str
    target_id: str
    attack_rule_source: str
    conditional_wound_probability: Callable[[TargetSurvivalState], Fraction]
    defence_plan: VerifiedDefencePlan
    defensive_prevention_eligible: bool = True

    def __post_init__(self):
        if not all(isinstance(getattr(self, name), str) and getattr(self, name).strip()
                   for name in ("event_id", "target_id", "attack_rule_source")):
            raise ValueError("event, target and verified attack rule source required")
        if not callable(self.conditional_wound_probability):
            raise TypeError("conditional_wound_probability must be callable")
        if not isinstance(self.defence_plan, VerifiedDefencePlan):
            raise TypeError("defence_plan must be VerifiedDefencePlan")
        if self.defensive_prevention_eligible is not True and (
            self.defence_plan.spend_one_fate_if_wounded
            or self.defence_plan.spend_one_will_if_wounded
        ):
            raise ValueError("defensive prevention cannot apply to this attack")


def evaluate_stateful_defended_wounds(
    target_id: str,
    initial: TargetSurvivalState,
    events: tuple[StatefulDefendedWound, ...],
) -> TargetSurvivalEvidence:
    if not isinstance(events, tuple) or any(
        not isinstance(e, StatefulDefendedWound) for e in events
    ):
        raise TypeError("events must be StatefulDefendedWound tuple")
    return evaluate_target_survival(
        target_id, initial,
        tuple(VerifiedTargetEvent(
            event_id=e.event_id,
            target_id=e.target_id,
            rule_source=e.attack_rule_source,
            transition=lambda state, event=e: single_wound_defence_transition(
                state, event.conditional_wound_probability(state), event.defence_plan
            ),
        ) for e in events),
    )
