"""DEV-078-PITS-B2: production adapter for Surprise Attack.

Author: Edward Turns (Project Lead)
This adapter establishes army eligibility and Azog's membership, then delegates
the declared Priority Phase event to the already tested B1 rule resolver.
Battlefield state is supplied explicitly, never inferred from the army roster.
"""
from __future__ import annotations
from dataclasses import dataclass

from army import Army
from pits_surprise_attack import (
    PITS_ARMY_ID, SURPRISE_ATTACK_RULE_ID,
    SurpriseAttackContext, SurpriseAttackResult, resolve_surprise_attack,
)


@dataclass(frozen=True)
class PitsPriorityPhaseRequest:
    azog_alive: bool
    azog_on_battlefield: bool
    already_used: bool
    declare_surprise_attack: bool
    opponent_declares_equivalent_priority_rule: bool = False
    simultaneous_roll_off_winner: str | None = None


def build_pits_surprise_attack_evidence(
    army: Army, army_list, *, request: PitsPriorityPhaseRequest
) -> SurpriseAttackResult:
    """Resolve a declared Pits Priority Phase, without changing army scores."""
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    if not isinstance(request, PitsPriorityPhaseRequest):
        raise TypeError("request must be PitsPriorityPhaseRequest")
    list_id = getattr(army_list, "id", None)
    if list_id != PITS_ARMY_ID:
        raise ValueError("Surprise Attack requires Pits of Dol Guldur")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError("army_list requires an army_rules sequence")
    rule_ids = tuple(getattr(rule, "id", None) for rule in rules)
    if SURPRISE_ATTACK_RULE_ID not in rule_ids:
        raise ValueError("Pits army lacks active Surprise Attack rule")
    if any(not isinstance(rule_id, str) or not rule_id.strip() for rule_id in rule_ids):
        raise ValueError("army rule identifiers must be nonblank")
    azog_models = [
        model for model in army.fielded_models()
        if getattr(getattr(model, "profile", None), "name", None) == "Azog the Defiler"
        or getattr(getattr(getattr(model, "configured_profile", None), "profile", None),
                   "name", None) == "Azog the Defiler"
    ]
    if len(azog_models) != 1:
        raise ValueError("Pits Surprise Attack requires one fielded Azog the Defiler")
    return resolve_surprise_attack(SurpriseAttackContext(
        army_list_id=list_id,
        active_army_rule_ids=rule_ids,
        azog_alive=request.azog_alive,
        azog_on_battlefield=request.azog_on_battlefield,
        already_used=request.already_used,
        declare_surprise_attack=request.declare_surprise_attack,
        opponent_declares_equivalent_priority_rule=request.opponent_declares_equivalent_priority_rule,
        simultaneous_roll_off_winner=request.simultaneous_roll_off_winner,
    ))
