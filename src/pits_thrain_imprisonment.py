"""DEV-078-PITS-C2: Thrain's Imprisonment contextual transition.

Author: Edward Turns (Project Lead)

This module delegates the original Shattered Spirit roll to the DEV-077
resolver, changing only a failed result when the Pits army rule is active
and the Keeper is within 6 inches. It does not infer battlefield positions,
change profiles, or modify capability/scenario scores.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from shattered_spirit_state import ShatteredSpiritResult, ShatteredSpiritState
from shattered_spirit_transition import resolve_shattered_spirit

PITS_ARMY_ID = "DG_PITS"
IMPRISONMENT_RULE_ID = "DG_THRAINS_IMPRISONMENT"


@dataclass(frozen=True)
class ThrainImprisonmentEvidence:
    original_state: ShatteredSpiritState
    effective_state: ShatteredSpiritState
    imprisonment_applied: bool
    thrain_counts_as_evil: bool
    keeper_distance_inches: float | None
    evidence_status: str = "declared_battlefield_context_not_calibrated"
    dashboard_score: None = None
    scenario_score: None = None


def resolve_thrain_imprisonment(
    *,
    army_list_id: str,
    active_army_rule_ids: tuple[str, ...] | list[str],
    first_die: int,
    second_die: int,
    intelligence: str,
    keeper_on_battlefield: bool,
    keeper_distance_inches: float | None,
) -> ThrainImprisonmentEvidence:
    """Return intrinsic and effective Shattered Spirit outcomes for Thrain.

    `keeper_distance_inches` is a declared physical measurement, not an
    inferred proximity. The rule is active only in a registered Pits list.
    A failed double is converted to NORMAL, never EMPOWERED.
    """
    if not isinstance(army_list_id, str) or not army_list_id.strip():
        raise ValueError("army_list_id must be nonblank")
    if not isinstance(active_army_rule_ids, (tuple, list)) or any(
        not isinstance(rule, str) or not rule.strip()
        for rule in active_army_rule_ids
    ):
        raise TypeError("active_army_rule_ids must be a sequence of nonblank strings")
    if not isinstance(keeper_on_battlefield, bool):
        raise TypeError("keeper_on_battlefield must be boolean")
    if keeper_distance_inches is not None:
        if isinstance(keeper_distance_inches, bool) or not isinstance(keeper_distance_inches, (int, float)):
            raise TypeError("keeper_distance_inches must be numeric or None")
        if not isfinite(keeper_distance_inches) or keeper_distance_inches < 0:
            raise ValueError("keeper_distance_inches must be finite and nonnegative")
    if keeper_on_battlefield and keeper_distance_inches is None:
        raise ValueError("Keeper on battlefield requires a declared distance")
    if not keeper_on_battlefield and keeper_distance_inches is not None:
        raise ValueError("Cannot supply distance for an absent Keeper")

    original = resolve_shattered_spirit(
        first_die=first_die, second_die=second_die, intelligence=intelligence
    )
    active = army_list_id == PITS_ARMY_ID and IMPRISONMENT_RULE_ID in active_army_rule_ids
    in_range = keeper_on_battlefield and keeper_distance_inches <= 6.0
    applied = bool(active and in_range and original.is_opponent_controlled)
    effective = (
        ShatteredSpiritState(result=ShatteredSpiritResult.NORMAL)
        if applied else original
    )
    return ThrainImprisonmentEvidence(
        original_state=original,
        effective_state=effective,
        imprisonment_applied=applied,
        thrain_counts_as_evil=active,
        keeper_distance_inches=keeper_distance_inches,
    )
