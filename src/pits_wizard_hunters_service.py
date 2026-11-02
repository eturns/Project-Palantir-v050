"""DEV-078-PITS-D2: Wizard Hunters real-army strike adapter.

Author: Edward Turns (Project Lead)
Attacker classification comes from the imported fielded profile, never caller
booleans. Enemy spell capability/Defence are explicitly supplied until an
opponent-army context is available. Diagnostic only; no score integration.
"""
from __future__ import annotations
from dataclasses import dataclass
from army import Army
from profile_classification import HeroicStatus
from pits_wizard_hunters import (
    PITS_ARMY_ID, WIZARD_HUNTERS_RULE_ID,
    WizardHuntersEvidence, calculate_wizard_hunters_strike,
)

@dataclass(frozen=True)
class WizardHuntersStrikeRequest:
    attacker_model_id: str
    defender_defence: int
    defender_can_cast_magical_powers: bool
    is_melee_strike: bool = True
    defender_is_enemy: bool = True


def build_pits_wizard_hunters_evidence(
    army: Army, army_list, *, request: WizardHuntersStrikeRequest
) -> WizardHuntersEvidence:
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    if not isinstance(request, WizardHuntersStrikeRequest):
        raise TypeError("request must be WizardHuntersStrikeRequest")
    if getattr(army_list, "id", None) != PITS_ARMY_ID:
        raise ValueError("Wizard Hunters requires Pits of Dol Guldur")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (list, tuple)):
        raise TypeError("army_list requires army_rules sequence")
    ids = tuple(getattr(r, "id", None) for r in rules)
    if any(not isinstance(r, str) or not r.strip() for r in ids):
        raise ValueError("army rule IDs must be nonblank strings")
    if WIZARD_HUNTERS_RULE_ID not in ids:
        raise ValueError("Pits army lacks active Wizard Hunters rule")
    if not isinstance(request.attacker_model_id, str) or not request.attacker_model_id.strip():
        raise TypeError("attacker_model_id must be nonblank")
    models = [m for m in army.fielded_models() if m.id == request.attacker_model_id]
    if len(models) != 1:
        raise ValueError("attacker model is not uniquely fielded")
    model = models[0]
    if model.configured_profile is None:
        raise ValueError("attacker must have a configured profile")
    profile = model.configured_profile.profile
    races = {str(r).upper() for r in profile.races}
    return calculate_wizard_hunters_strike(
        army_list_id=army_list.id,
        active_army_rule_ids=ids,
        attacker_is_friendly=True,
        attacker_is_orc=("ORC" in races),
        attacker_is_warrior=(profile.heroic_status is HeroicStatus.WARRIOR),
        defender_is_enemy=request.defender_is_enemy,
        defender_can_cast_magical_powers=request.defender_can_cast_magical_powers,
        is_melee_strike=request.is_melee_strike,
        attacker_strength=model.configured_profile.profile.strength,
        defender_defence=request.defender_defence,
    )
