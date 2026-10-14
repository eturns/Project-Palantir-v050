"""DEV-077S-I2-H1-B: evidence-gated Control opportunity and action legality.

Diagnostic only. Callers must supply independently verified rules, target and
battlefield evidence. No dice rolls, board positions, or scoring are invented.
Confirmed outcomes are applied by the existing H1-A state module.
"""
from dataclasses import dataclass
from enum import Enum

from control_effect_state import (
    ControlState,
    apply_confirmed_control_effect,
    restrictions_for_target,
)
from hero_hunting_control_spells import ControlSpellEvidence


class EvidenceVerdict(Enum):
    VERIFIED_TRUE = "verified_true"
    VERIFIED_FALSE = "verified_false"
    UNKNOWN = "unknown"


class ControlAction(Enum):
    ACTIVATE = "activate"
    SHOOT = "shoot"
    HEROIC_ACTION = "heroic_action"
    ACTIVE_ABILITY = "active_ability"
    STRIKE_AFTER_WINNING_DUEL = "strike_after_winning_duel"
    MOVE_FURTHER = "move_further"


class ActionLegality(Enum):
    PERMITTED_BY_CONTROL = "permitted_by_control"
    BLOCKED_BY_CONTROL = "blocked_by_control"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True)
class ControlOpportunity:
    """Independent checks, not forecasts or probabilities.

    Casting availability and target legality must both be explicitly verified.
    Success means the casting/resistance outcome is already determined.
    UNKNOWN is not equivalent to failure, success or a zero-valued metric.
    """
    caster_can_attempt: EvidenceVerdict
    target_is_legal: EvidenceVerdict
    effect_succeeded: EvidenceVerdict

    def __post_init__(self) -> None:
        for value in (self.caster_can_attempt, self.target_is_legal, self.effect_succeeded):
            if not isinstance(value, EvidenceVerdict):
                raise TypeError("opportunity verdicts must be EvidenceVerdict")


@dataclass(frozen=True)
class ControlApplicationResult:
    state: ControlState
    applied: bool
    reason: str


def resolve_control_application(
    state: ControlState,
    *,
    effect_id: str,
    source_id: str,
    target_id: str,
    evidence: ControlSpellEvidence,
    opportunity: ControlOpportunity,
) -> ControlApplicationResult:
    """Only a verified, successful and legal effect may alter active state.

    Verified failures return the *same* state with a diagnostic reason.
    Unknown prerequisites likewise leave state untouched. H1-A performs the
    actual state transition and checks supported spell evidence.
    """
    if not isinstance(state, ControlState):
        raise TypeError("state must be ControlState")
    if not isinstance(opportunity, ControlOpportunity):
        raise TypeError("opportunity must be ControlOpportunity")
    if not isinstance(evidence, ControlSpellEvidence):
        raise TypeError("evidence must be ControlSpellEvidence")
    for name, value in (("effect_id", effect_id), ("source_id", source_id), ("target_id", target_id)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{name} must be nonblank")
    if any(effect.effect_id == effect_id for effect in state.active_effects):
        raise ValueError("effect_id already exists")

    checks = (
        ("caster_unavailable", opportunity.caster_can_attempt),
        ("illegal_target", opportunity.target_is_legal),
        ("effect_failed", opportunity.effect_succeeded),
    )
    for reason, verdict in checks:
        if verdict is EvidenceVerdict.VERIFIED_FALSE:
            return ControlApplicationResult(state, False, reason)
    if any(verdict is EvidenceVerdict.UNKNOWN for _, verdict in checks):
        return ControlApplicationResult(state, False, "unresolved_evidence")

    result = apply_confirmed_control_effect(
        state,
        effect_id=effect_id,
        source_id=source_id,
        target_id=target_id,
        evidence=evidence,
        cast_and_resist_resolved=True,
        target_legality_verified=True,
    )
    return ControlApplicationResult(result, True, "confirmed_applied")


def evaluate_control_action(
    state: ControlState,
    *,
    target_id: str,
    action: ControlAction,
    other_legality: EvidenceVerdict = EvidenceVerdict.UNKNOWN,
) -> ActionLegality:
    """Determine Control restrictions only; never declare full game legality.

    If Control blocks the action, other game checks cannot make it legal.
    Without a Control block, other_legality must explicitly confirm the
    remaining rules before returning PERMITTED_BY_CONTROL.
    """
    if not isinstance(action, ControlAction):
        raise TypeError("action must be ControlAction")
    if not isinstance(other_legality, EvidenceVerdict):
        raise TypeError("other_legality must be EvidenceVerdict")
    restrictions = restrictions_for_target(state, target_id=target_id)
    blocked = {
        ControlAction.ACTIVATE: restrictions.activation_blocked,
        ControlAction.SHOOT: restrictions.shooting_blocked,
        ControlAction.HEROIC_ACTION: restrictions.heroic_actions_blocked,
        ControlAction.ACTIVE_ABILITY: restrictions.active_abilities_blocked,
        ControlAction.STRIKE_AFTER_WINNING_DUEL: restrictions.strikes_when_winning_duel_blocked,
        ControlAction.MOVE_FURTHER: restrictions.further_movement_blocked,
    }[action]
    if blocked or other_legality is EvidenceVerdict.VERIFIED_FALSE:
        return ActionLegality.BLOCKED_BY_CONTROL if blocked else ActionLegality.UNRESOLVED
    if other_legality is EvidenceVerdict.VERIFIED_TRUE:
        return ActionLegality.PERMITTED_BY_CONTROL
    return ActionLegality.UNRESOLVED
