"""DEV-078-AH-B2 — Real-army Relentless Hunters entitlement inventory.

Author: Edward Turns (Project Lead)
Read-only, diagnostic-only; no terrain state or score changes.
"""
from dataclasses import dataclass
from army import Army
from relentless_hunters import (
    ARMY_LIST_ID, RULE_ID, GRANTED_RULE_IDS, resolve_relentless_hunters
)

@dataclass(frozen=True)
class RelentlessHuntersArmyInventory:
    army_list_id: str
    source_rule_id: str | None
    model_count: int
    eligible_model_ids: tuple[str, ...]
    granted_rule_ids: tuple[str, ...]
    status: str = "army_entitlement_not_terrain_simulation"
    dashboard_score: None = None
    scenario_score: None = None


def build_relentless_hunters_inventory(army: Army, army_list):
    if not isinstance(army, Army):
        raise TypeError("Relentless Hunters inventory requires a real Army")
    list_id = getattr(army_list, "id", None)
    if not isinstance(list_id, str) or not list_id.strip():
        raise ValueError("Registered army_list.id required")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (tuple, list)):
        raise TypeError("Registered army_list.army_rules required")
    rule_ids = tuple(getattr(rule, "id", None) for rule in rules)
    if any(not isinstance(rule_id, str) or not rule_id.strip() for rule_id in rule_ids):
        raise ValueError("Registered army rules require nonblank identifiers")
    active = list_id == ARMY_LIST_ID and RULE_ID in rule_ids
    ids = tuple(model.id for model in army.fielded_models() if model.counts_as_model)
    if len(ids) != len(set(ids)):
        raise ValueError("Fielded model IDs must be unique")
    for model_id in ids:
        check = resolve_relentless_hunters(
            army_list_id=list_id, active_army_rule_ids=rule_ids,
            model_is_friendly=True
        )
        if check.granted != active:
            raise ValueError("Unexpected Relentless Hunters entitlement mismatch")
    return RelentlessHuntersArmyInventory(
        army_list_id=list_id,
        source_rule_id=RULE_ID if active else None,
        model_count=len(ids),
        eligible_model_ids=ids if active else (),
        granted_rule_ids=GRANTED_RULE_IDS if active else (),
    )
