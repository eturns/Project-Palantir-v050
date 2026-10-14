"""DEV-077S-I2-H1-A: diagnostic-only, confirmed Control effect lifecycle.

Consumes the existing Hero Hunting spell evidence without modifying that
pipeline. It does not resolve casting, target legality, physical movement,
initiative, or scoring. Unverified effects cannot enter an active state.
"""
from dataclasses import dataclass, replace
from enum import Enum
from fractions import Fraction

from hero_hunting_control_spells import ControlSpellEvidence


class ControlExpiry(Enum):
    END_PHASE = "end_phase"
    TURN_END = "turn_end"


@dataclass(frozen=True)
class ActiveControlEffect:
    effect_id: str
    source_id: str
    target_id: str
    spell_id: str
    expiry: ControlExpiry
    activation_blocked: bool
    shooting_blocked: bool
    heroic_actions_blocked: bool
    active_abilities_blocked: bool
    strikes_when_winning_duel_blocked: bool
    compelled_max_movement_inches: Fraction | None
    further_movement_blocked: bool
    evidence_status: str


@dataclass(frozen=True)
class ControlState:
    active_effects: tuple[ActiveControlEffect, ...] = ()


@dataclass(frozen=True)
class TargetControlRestrictions:
    target_id: str
    activation_blocked: bool = False
    shooting_blocked: bool = False
    heroic_actions_blocked: bool = False
    active_abilities_blocked: bool = False
    strikes_when_winning_duel_blocked: bool = False
    compelled_max_movement_inches: Fraction | None = None
    further_movement_blocked: bool = False
    contributing_effect_ids: tuple[str, ...] = ()


def _nonblank(value: str, label: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonblank")


def apply_confirmed_control_effect(
    state: ControlState,
    *,
    effect_id: str,
    source_id: str,
    target_id: str,
    evidence: ControlSpellEvidence,
    cast_and_resist_resolved: bool,
    target_legality_verified: bool,
) -> ControlState:
    """Record a verified outcome, never a probability-weighted assumption."""
    if not isinstance(state, ControlState):
        raise TypeError("state must be ControlState")
    for label, value in (("effect_id", effect_id), ("source_id", source_id), ("target_id", target_id)):
        _nonblank(value, label)
    if not isinstance(evidence, ControlSpellEvidence):
        raise TypeError("evidence must be ControlSpellEvidence")
    if type(cast_and_resist_resolved) is not bool or type(target_legality_verified) is not bool:
        raise TypeError("resolution and legality flags must be bool")
    if not cast_and_resist_resolved or not target_legality_verified:
        raise ValueError("control effect cannot be applied without verified success and legality")
    if any(effect.effect_id == effect_id for effect in state.active_effects):
        raise ValueError("effect_id already exists")

    if evidence.spell_id == "TRANSFIX" and evidence.duration == "temporary_until_end_phase":
        expiry = ControlExpiry.END_PHASE
    elif evidence.spell_id == "COMPEL" and evidence.duration == "instant_with_movement_restriction_until_turn_end":
        expiry = ControlExpiry.TURN_END
    else:
        raise ValueError("unsupported spell or effect duration")
    if evidence.evidence_status not in (
        "verified_conditional_control_effect",
        "verified_compelled_movement_ceiling",
        "engaged_target_cannot_be_moved_out_of_combat",
    ):
        raise ValueError("unsupported evidence status")

    effect = ActiveControlEffect(
        effect_id=effect_id, source_id=source_id, target_id=target_id,
        spell_id=evidence.spell_id, expiry=expiry,
        activation_blocked=evidence.activation_blocked,
        shooting_blocked=evidence.shooting_blocked,
        heroic_actions_blocked=evidence.heroic_actions_blocked,
        active_abilities_blocked=evidence.active_abilities_blocked,
        strikes_when_winning_duel_blocked=evidence.strikes_when_winning_duel_blocked,
        compelled_max_movement_inches=evidence.compelled_max_movement_inches,
        further_movement_blocked=evidence.further_movement_blocked,
        evidence_status=evidence.evidence_status,
    )
    return replace(state, active_effects=state.active_effects + (effect,))


def expire_control_effects(state: ControlState, *, boundary: ControlExpiry) -> ControlState:
    """End Phase expires End Phase effects; turn end clears all temporary effects."""
    if not isinstance(state, ControlState):
        raise TypeError("state must be ControlState")
    if not isinstance(boundary, ControlExpiry):
        raise TypeError("boundary must be ControlExpiry")
    if boundary is ControlExpiry.TURN_END:
        return ControlState()
    return replace(state, active_effects=tuple(
        effect for effect in state.active_effects if effect.expiry is not ControlExpiry.END_PHASE
    ))


def restrictions_for_target(state: ControlState, *, target_id: str) -> TargetControlRestrictions:
    if not isinstance(state, ControlState):
        raise TypeError("state must be ControlState")
    _nonblank(target_id, "target_id")
    effects = tuple(effect for effect in state.active_effects if effect.target_id == target_id)
    ceilings = tuple(effect.compelled_max_movement_inches for effect in effects
                     if effect.compelled_max_movement_inches is not None)
    return TargetControlRestrictions(
        target_id=target_id,
        activation_blocked=any(effect.activation_blocked for effect in effects),
        shooting_blocked=any(effect.shooting_blocked for effect in effects),
        heroic_actions_blocked=any(effect.heroic_actions_blocked for effect in effects),
        active_abilities_blocked=any(effect.active_abilities_blocked for effect in effects),
        strikes_when_winning_duel_blocked=any(effect.strikes_when_winning_duel_blocked for effect in effects),
        compelled_max_movement_inches=min(ceilings) if ceilings else None,
        further_movement_blocked=any(effect.further_movement_blocked for effect in effects),
        contributing_effect_ids=tuple(effect.effect_id for effect in effects),
    )
