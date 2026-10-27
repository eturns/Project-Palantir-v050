"""DEV-077-TT-D2E: Three Trolls 'Keep 'em for later' state resolver.

Authoritative source: MESBG Armies of the Hobbit (2024), pp. 140-142.
This module represents capture and persistent paralysis; it does not
simulate the Paralyse Magical Power's separate recovery mechanism.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum

TROLL_PROFILE_IDS = frozenset({"TT_BILL", "TT_BERT", "TT_TOM"})


class CaptureAction(str, Enum):
    STRIKES = "strikes"
    BRUTAL_POWER_ATTACK = "brutal_power_attack"
    KEEP_FOR_LATER = "keep_for_later"


@dataclass(frozen=True)
class CaptiveState:
    """Snapshot of a model: other game-state effects are owned by the caller."""
    model_id: str
    base_size_mm: int
    is_enemy: bool
    involved_in_combat: bool
    paralysed: bool = False
    alive: bool = True
    captured_by_troll_id: str | None = None
    counts_as_casualty: bool = False

    def __post_init__(self) -> None:
        if not self.model_id:
            raise ValueError("model_id must not be empty")
        if self.base_size_mm <= 0:
            raise ValueError("base_size_mm must be positive")


@dataclass(frozen=True)
class CaptureContext:
    troll_profile_id: str
    troll_model_id: str
    won_duel: bool
    action: CaptureAction
    target: CaptiveState


@dataclass(frozen=True)
class CaptureOutcome:
    target: CaptiveState
    strikes_replaced: bool
    brutal_power_attack_replaced: bool
    paralyse_effect_applied: bool
    independent_of_captor_will_or_survival: bool


def can_keep_for_later(context: CaptureContext) -> bool:
    """Whether the model can use its capture alternative at this Duel."""
    if not isinstance(context.action, CaptureAction):
        raise ValueError("Unknown combat action")
    return (
        context.troll_profile_id in TROLL_PROFILE_IDS
        and bool(context.troll_model_id)
        and context.won_duel
        and context.action is CaptureAction.KEEP_FOR_LATER
        and context.target.alive
        and context.target.is_enemy
        and context.target.involved_in_combat
        and context.target.base_size_mm == 25
    )


def apply_keep_for_later(context: CaptureContext) -> CaptureOutcome:
    """Capture an eligible 25mm enemy instead of Strikes or a BPA.

    The target receives persistent paralysis. Captor death or Will depletion
    must not automatically end it. Ordinary recovery tests remain external.
    """
    if not can_keep_for_later(context):
        raise ValueError("Keep 'em for later is not legal in this combat")
    captured = replace(
        context.target,
        paralysed=True,
        captured_by_troll_id=context.troll_model_id,
    )
    return CaptureOutcome(
        target=captured,
        strikes_replaced=True,
        brutal_power_attack_replaced=True,
        paralyse_effect_applied=True,
        independent_of_captor_will_or_survival=True,
    )


def resolve_end_of_game_captive(target: CaptiveState) -> CaptiveState:
    """Still-paralysed captured targets count as slain casualties at game end.

    If a target has recovered, this rule does not make it a casualty.
    Does not independently assert that an already-dead model is alive.
    """
    if target.captured_by_troll_id and target.paralysed:
        return replace(target, alive=False, counts_as_casualty=True)
    return target
