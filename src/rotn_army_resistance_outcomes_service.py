"""DEV-078-ROTN-D5 Stage 2: map explicit resistance requests to fielded models.

Author: Edward Turns (Project Lead)
Entitlement is derived from canonical active army rules. Other free dice
are explicitly declared by the caller; no target or casting event inferred.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

from army import Army
from magic_resistance_outcomes import MagicResistanceOutcome, resolve_magic_resistance
from rotn_army_magic_service_adapter import build_army_magic_resistance_inventory


@dataclass(frozen=True)
class ResistanceRequest:
    cast_highest: int
    will_available: int
    will_spent: int = 0
    other_free_die_sources: tuple[str, ...] = ()
    hero: bool = False
    directly_targeted: bool = True


@dataclass(frozen=True)
class ArmyResistanceOutcomeEvidence:
    army_list_id: str
    source_rule_id: str | None
    outcomes_by_model_id: tuple[tuple[str, MagicResistanceOutcome], ...]
    evidence_status: str = "declared_resist_tests_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def build_army_resistance_outcomes(
    army: Army,
    army_list,
    *,
    requests_by_model_id: Mapping[str, ResistanceRequest],
) -> ArmyResistanceOutcomeEvidence:
    """Resolve caller-supplied resist tests, one per explicitly targeted model."""
    if not isinstance(army, Army):
        raise TypeError("army must be an Army")
    if not isinstance(requests_by_model_id, Mapping):
        raise TypeError("requests_by_model_id must be a mapping")
    inventory = build_army_magic_resistance_inventory(army, army_list)
    fielded_ids = {model.id for model in army.fielded_models()}
    eligible = set(inventory.eligible_model_ids)
    outcomes = []
    for model_id, request in requests_by_model_id.items():
        if not isinstance(model_id, str) or not model_id.strip():
            raise TypeError("target model ID must be a nonblank string")
        if model_id not in fielded_ids:
            raise ValueError(f"target model ID is not fielded: {model_id}")
        if not isinstance(request, ResistanceRequest):
            raise TypeError("resistance requests must be ResistanceRequest instances")
        outcome = resolve_magic_resistance(
            cast_highest=request.cast_highest,
            will_available=request.will_available,
            will_spent=request.will_spent,
            resistant_to_magic=(model_id in eligible),
            other_free_die_sources=request.other_free_die_sources,
            hero=request.hero,
            directly_targeted=request.directly_targeted,
        )
        outcomes.append((model_id, outcome))
    return ArmyResistanceOutcomeEvidence(
        army_list_id=inventory.army_list_id,
        source_rule_id=inventory.source_rule_id,
        outcomes_by_model_id=tuple(outcomes),
    )
