"""DEV-078-ROTN-C3: army-wide Resistant to Magic entitlement evidence.

This module resolves whether the army-list ability grants the special rule to a
friendly model. It does not simulate a Resist test, spend Will, modify a roll,
or affect capability scores. Both 2024 Hobbit army lists use the same grant.
"""
from __future__ import annotations
from dataclasses import dataclass

_ARMY_GRANTS = {
    "DG_ROTN": "DG_POWER_OF_THE_NECROMANCER",
    "DG_PITS": "DG_MAGICAL_VOID",
}


@dataclass(frozen=True)
class ArmyMagicResistanceEvidence:
    army_list_id: str
    model_is_friendly: bool
    granted: bool
    source_rule_id: str | None
    status: str = "rule_entitlement_only_not_resist_test"
    dashboard_score: None = None
    scenario_score: None = None


def resolve_army_magic_resistance(
    *, army_list_id: str, active_army_rule_ids: tuple[str, ...] | list[str] | set[str],
    model_is_friendly: bool,
) -> ArmyMagicResistanceEvidence:
    """Declare the army-wide grant only for an explicitly active matching rule.

    Do not infer rule activation solely from the army-list name. The caller
    supplies canonical active rule IDs and friendliness; no battlefield state
    is fabricated.
    """
    if not isinstance(army_list_id, str) or not army_list_id.strip():
        raise ValueError("army_list_id must be a nonblank string")
    if not isinstance(model_is_friendly, bool):
        raise TypeError("model_is_friendly must be boolean")
    if not isinstance(active_army_rule_ids, (tuple, list, set, frozenset)):
        raise TypeError("active_army_rule_ids must be a collection of strings")
    if any(not isinstance(r, str) or not r.strip() for r in active_army_rule_ids):
        raise ValueError("active_army_rule_ids must contain nonblank strings")
    rule_id = _ARMY_GRANTS.get(army_list_id)
    granted = bool(model_is_friendly and rule_id and rule_id in active_army_rule_ids)
    return ArmyMagicResistanceEvidence(
        army_list_id=army_list_id,
        model_is_friendly=model_is_friendly,
        granted=granted,
        source_rule_id=rule_id if granted else None,
    )
