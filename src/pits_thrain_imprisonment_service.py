"""DEV-078-PITS-C2 Stage 2: real-army Thrain's Imprisonment adapter.

Author: Edward Turns (Project Lead)
"""
from __future__ import annotations

from dataclasses import dataclass
from army import Army
from pits_thrain_imprisonment import (
    PITS_ARMY_ID, IMPRISONMENT_RULE_ID, ThrainImprisonmentEvidence,
    resolve_thrain_imprisonment,
)

@dataclass(frozen=True)
class PitsThrainTestRequest:
    first_die: int
    second_die: int
    intelligence: str
    keeper_on_battlefield: bool
    keeper_distance_inches: float | None


def build_pits_thrain_imprisonment_evidence(
    army: Army, army_list, *, request: PitsThrainTestRequest
) -> ThrainImprisonmentEvidence:
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    if not isinstance(request, PitsThrainTestRequest):
        raise TypeError("request must be PitsThrainTestRequest")
    if getattr(army_list, "id", None) != PITS_ARMY_ID:
        raise ValueError("Thrain's Imprisonment requires Pits of Dol Guldur")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError("army_list requires army_rules sequence")
    rule_ids = tuple(getattr(rule, "id", None) for rule in rules)
    if IMPRISONMENT_RULE_ID not in rule_ids:
        raise ValueError("Pits army lacks active Thrain's Imprisonment rule")
    if any(not isinstance(r, str) or not r.strip() for r in rule_ids):
        raise ValueError("army rule IDs must be nonblank strings")
    names = [
        getattr(getattr(m.configured_profile, "profile", None), "name", None)
        for m in army.fielded_models() if m.configured_profile is not None
    ]
    if names.count("Thráin the Broken") + names.count("Thrain the Broken") != 1:
        raise ValueError("Pits army requires exactly one Thrain the Broken")
    if names.count("The Keeper of the Dungeons") != 1:
        raise ValueError("Pits army requires exactly one Keeper of the Dungeons")
    return resolve_thrain_imprisonment(
        army_list_id=army_list.id,
        active_army_rule_ids=rule_ids,
        first_die=request.first_die,
        second_die=request.second_die,
        intelligence=request.intelligence,
        keeper_on_battlefield=request.keeper_on_battlefield,
        keeper_distance_inches=request.keeper_distance_inches,
    )
