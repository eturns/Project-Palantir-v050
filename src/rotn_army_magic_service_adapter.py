"""DEV-078-ROTN-C4: opt-in army-analysis service adapter.

Author: Edward Turns (Project Lead)

Adds per-fielded-model Resistant to Magic entitlement evidence to the normal
army analysis result. Does not resolve resistance dice, consume Will, modify
metrics, or alter calibration. Existing service remains unchanged.
"""
from __future__ import annotations

from dataclasses import dataclass

from army import Army
from army_wide_magic_resistance import resolve_army_magic_resistance


@dataclass(frozen=True)
class ArmyMagicResistanceInventory:
    army_list_id: str
    source_rule_id: str | None
    eligible_model_ids: tuple[str, ...]
    model_count: int
    evidence_status: str = "entitlement_only_not_resistance_outcome"
    dashboard_score: None = None
    scenario_score: None = None


def build_army_magic_resistance_inventory(army: Army, army_list) -> ArmyMagicResistanceInventory:
    """Resolve explicit army-list grants for all distinct fielded models."""
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    list_id = getattr(army_list, "id", None)
    if not isinstance(list_id, str) or not list_id.strip():
        raise TypeError("army_list requires a nonblank id")
    rules = getattr(army_list, "army_rules", None)
    if not isinstance(rules, (list, tuple)):
        raise TypeError("army_list requires an army_rules sequence")
    rule_ids = tuple(getattr(rule, "id", None) for rule in rules)
    if any(not isinstance(rid, str) or not rid.strip() for rid in rule_ids):
        raise ValueError("army rule IDs must be nonblank strings")
    models = army.fielded_models()
    ids = tuple(model.id for model in models)
    if len(ids) != len(set(ids)):
        raise ValueError("fielded model IDs must be distinct")
    eligibility = resolve_army_magic_resistance(
        army_list_id=list_id, active_army_rule_ids=rule_ids,
        model_is_friendly=True,
    )
    return ArmyMagicResistanceInventory(
        army_list_id=list_id,
        source_rule_id=eligibility.source_rule_id,
        eligible_model_ids=ids if eligibility.granted else (),
        model_count=len(ids),
    )


def analyse_imported_army(*args, **kwargs):
    """Lazy compatibility shim: avoids circular service imports."""
    from services.army_analysis_service import analyse_imported_army as service
    return service(*args, **kwargs)

def analyse_imported_army_with_magic_resistance(
    army, army_list, points_limit, metric_thresholds, **kwargs
):
    """Opt-in service entrypoint. Preserve all original analysis keys and scores."""
    result = analyse_imported_army(
        army, army_list, points_limit, metric_thresholds, **kwargs
    )
    if not isinstance(army, Army):
        return result
    inventory = build_army_magic_resistance_inventory(army, army_list)
    if inventory.source_rule_id is None:
        return result
    existing = result.get("mechanical_army_magic_resistance")
    if existing is not None:
        if existing != inventory:
            raise ValueError("inconsistent magic resistance evidence")
        return result
    return {**result, "mechanical_army_magic_resistance": inventory}
