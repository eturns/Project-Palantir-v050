"""DEV-078-AH-B1 — Relentless Hunters army-wide entitlement.

Author: Edward Turns (Project Lead)

2024 army rule: all models in Azog's Hunters gain Woodland Creature and
Mountain Dweller. This is a strictly uncalibrated entitlement contract:
it does not guess terrain, movement paths, or change mobility scores.
"""
from dataclasses import dataclass

ARMY_LIST_ID = "AZOGS_HUNTERS"
RULE_ID = "DG_RELENTLESS_HUNTERS"
GRANTED_RULE_IDS = ("WOODLAND_CREATURE", "MOUNTAIN_DWELLER")


@dataclass(frozen=True)
class RelentlessHuntersEvidence:
    army_list_id: str
    model_is_friendly: bool
    granted: bool
    granted_rule_ids: tuple[str, ...]
    source_rule_id: str | None
    status: str = "army_rule_entitlement_only_not_terrain_simulation"
    dashboard_score: None = None
    scenario_score: None = None


def resolve_relentless_hunters(
    *,
    army_list_id: str,
    active_army_rule_ids: tuple[str, ...] | list[str] | set[str] | frozenset[str],
    model_is_friendly: bool,
) -> RelentlessHuntersEvidence:
    """Resolve the grant without inferring army membership or battlefield state."""
    if not isinstance(army_list_id, str) or not army_list_id.strip():
        raise ValueError("army_list_id must be a nonblank string")
    if not isinstance(model_is_friendly, bool):
        raise TypeError("model_is_friendly must be boolean")
    if not isinstance(active_army_rule_ids, (tuple, list, set, frozenset)):
        raise TypeError("active_army_rule_ids must be a collection of strings")
    if any(not isinstance(r, str) or not r.strip() for r in active_army_rule_ids):
        raise ValueError("active_army_rule_ids must contain nonblank strings")
    granted = (
        army_list_id == ARMY_LIST_ID
        and RULE_ID in active_army_rule_ids
        and model_is_friendly
    )
    return RelentlessHuntersEvidence(
        army_list_id=army_list_id,
        model_is_friendly=model_is_friendly,
        granted=granted,
        granted_rule_ids=GRANTED_RULE_IDS if granted else (),
        source_rule_id=RULE_ID if granted else None,
    )
