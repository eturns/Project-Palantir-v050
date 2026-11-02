"""DEV-078-PITS-B: declared Surprise Attack Priority Phase resolution.

Author: Edward Turns (Project Lead)

Deterministic, conditional battlefield evidence; not a turn simulator and
not an input to legacy capability/scenario scores. Call once per Priority
Phase with observed Azog state and declarations. The caller owns persistence
of the returned once-per-game usage flag.
"""
from __future__ import annotations
from dataclasses import dataclass

PITS_ARMY_ID = 'DG_PITS'
SURPRISE_ATTACK_RULE_ID = 'DG_SURPRISE_ATTACK'


@dataclass(frozen=True)
class SurpriseAttackContext:
    army_list_id: str
    active_army_rule_ids: tuple[str, ...]
    azog_alive: bool
    azog_on_battlefield: bool
    already_used: bool
    declare_surprise_attack: bool
    opponent_declares_equivalent_priority_rule: bool = False
    # Only relevant when both sides activate competing priority abilities.
    # 'pits' or 'opponent' is the *observed* result of the normal roll-off.
    simultaneous_roll_off_winner: str | None = None


@dataclass(frozen=True)
class SurpriseAttackResult:
    declared: bool
    used_after_phase: bool
    priority_winner: str | None
    pits_must_take_priority: bool
    opposing_heroic_moves_prohibited: bool
    simultaneous_resolution_required: bool
    evidence_status: str = 'declared_priority_phase_not_calibrated'
    dashboard_score: None = None
    scenario_score: None = None


def resolve_surprise_attack(context: SurpriseAttackContext) -> SurpriseAttackResult:
    """Resolve activation and known priority outcome without inventing dice.

    The opponent's equivalent ability is represented only as a declared
    competing automatic-priority rule. An ordinary Priority roll is external.
    """
    if not isinstance(context, SurpriseAttackContext):
        raise TypeError('context must be SurpriseAttackContext')
    if not isinstance(context.army_list_id, str) or not context.army_list_id.strip():
        raise ValueError('army_list_id must be a nonblank string')
    if not isinstance(context.active_army_rule_ids, tuple) or any(
        not isinstance(rule, str) or not rule.strip() for rule in context.active_army_rule_ids
    ):
        raise TypeError('active_army_rule_ids must be a tuple of nonblank strings')
    for name in ('azog_alive', 'azog_on_battlefield', 'already_used',
                 'declare_surprise_attack', 'opponent_declares_equivalent_priority_rule'):
        if not isinstance(getattr(context, name), bool):
            raise TypeError(f'{name} must be bool')
    winner = context.simultaneous_roll_off_winner
    if winner is not None and winner not in ('pits', 'opponent'):
        raise ValueError("simultaneous_roll_off_winner must be 'pits', 'opponent', or None")
    simultaneous = context.declare_surprise_attack and context.opponent_declares_equivalent_priority_rule
    if winner is not None and not simultaneous:
        raise ValueError('roll-off winner can only be supplied for simultaneous declarations')
    if not context.declare_surprise_attack:
        return SurpriseAttackResult(False, context.already_used, None, False, False, False)
    if context.army_list_id != PITS_ARMY_ID or SURPRISE_ATTACK_RULE_ID not in context.active_army_rule_ids:
        raise ValueError('Surprise Attack is not active for this army list')
    if context.already_used:
        raise ValueError('Surprise Attack has already been used')
    if not context.azog_alive or not context.azog_on_battlefield:
        raise ValueError('Azog must be alive and on the battlefield')
    if simultaneous:
        # Both abilities are consumed even if the opposing player wins.
        # Do not award Priority or determine movement eligibility until the
        # actual roll-off outcome is supplied.
        return SurpriseAttackResult(
            True, True, winner, winner == 'pits',
            True, winner is None,
        )
    return SurpriseAttackResult(True, True, 'pits', True, True, False)
