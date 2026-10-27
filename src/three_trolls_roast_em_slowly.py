"""DEV-077-TT-D2B: Bert's Roast 'em Slowly Brutal Power Attack.

Authority: MESBG Armies of the Hobbit (2024), Bert profile, PDF page 141.
An explicit effect resolver only: no inferred damage, position or scoring.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


BERT_PROFILE_ID = "TT_BERT"
ROAST_EM_SLOWLY_RULE_ID = "ROAST_EM_SLOWLY"
CAMPFIRE_RANGE_INCHES = 6.0


@dataclass(frozen=True)
class RoastEmSlowlyContext:
    """Facts supplied by the battle-state caller, not inferred by the resolver.

    target_id identifies an enemy already involved in Bert's combat.
    campfire_distance_inches is Bert-to-Campfire distance.
    """

    attacker_profile_id: str
    target_id: str
    attacker_won_duel: bool
    target_is_enemy_in_combat: bool
    campfire_present: bool
    campfire_distance_inches: float | None
    alternative_attack_already_used: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.attacker_profile_id, str) or not self.attacker_profile_id:
            raise ValueError("Attacker profile ID is required.")
        if not isinstance(self.target_id, str) or not self.target_id:
            raise ValueError("Target ID is required.")
        for name in ("attacker_won_duel", "target_is_enemy_in_combat", "campfire_present", "alternative_attack_already_used"):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be a boolean.")
        distance = self.campfire_distance_inches
        if distance is not None and (
            isinstance(distance, bool)
            or not isinstance(distance, (int, float))
            or not isfinite(distance)
            or distance < 0
        ):
            raise ValueError("Campfire distance must be finite and nonnegative.")


@dataclass(frozen=True)
class RoastEmSlowlyResult:
    """Instructions for a battle-state consumer; not automatic state mutation."""

    target_id: str
    replace_normal_strikes: bool
    relocate_target_into_campfire_base_contact: bool
    set_target_ablaze: bool
    damage_evaluated: bool = False


def resolve_roast_em_slowly(context: RoastEmSlowlyContext) -> RoastEmSlowlyResult | None:
    """Return the conditional effect, or None when use is unavailable.

    The *2024 profile* requires Bert to be within 6 inches of a Campfire.
    This action replaces Strikes; it does not independently roll damage.
    """
    if context.attacker_profile_id != BERT_PROFILE_ID:
        return None
    if not context.attacker_won_duel or context.alternative_attack_already_used:
        return None
    if not context.target_is_enemy_in_combat:
        return None
    if not context.campfire_present or context.campfire_distance_inches is None:
        return None
    if context.campfire_distance_inches > CAMPFIRE_RANGE_INCHES:
        return None
    return RoastEmSlowlyResult(
        target_id=context.target_id,
        replace_normal_strikes=True,
        relocate_target_into_campfire_base_contact=True,
        set_target_ablaze=True,
    )
