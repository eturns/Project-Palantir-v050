"""DEV-078-ROTN-C1 — Pure Rise of the Necromancer cast-sequence rules.

2024 Armies of the Hobbit p.154 (printed): the Necromancer may attempt
up to two different Magical Powers on activation, and may not target the
same enemy model twice. This module makes no assumptions about casting
success, Will expenditure, range, or battlefield turn scheduling.

No metrics, dashboard, or calibration integration is performed here.
"""
from __future__ import annotations

from dataclasses import dataclass

NECROMANCER_PROFILE_ID = "DG_NEC"
POWER_RULE_ID = "DG_POWER_OF_THE_NECROMANCER"


@dataclass(frozen=True)
class CastDeclaration:
    spell_id: str
    target_model_id: str | None = None
    target_is_enemy: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.spell_id, str) or not self.spell_id.strip():
            raise ValueError("spell_id must be non-empty")
        if self.target_model_id is not None and (
            not isinstance(self.target_model_id, str) or not self.target_model_id.strip()
        ):
            raise ValueError("target_model_id must be non-empty when supplied")
        if not isinstance(self.target_is_enemy, bool):
            raise TypeError("target_is_enemy must be boolean")
        if self.target_is_enemy and self.target_model_id is None:
            raise ValueError("enemy target requires a target_model_id")


def validate_cast_sequence(
    declarations: tuple[CastDeclaration, ...],
    *,
    caster_profile_id: str,
    active_army_rule_ids: frozenset[str] = frozenset(),
) -> None:
    """Raise ValueError for a forbidden sequence, otherwise return None.

    The normal single-cast cap applies unless the canonical army rule is
    active on the Necromancer. An eligible second spell must be distinct;
    explicitly identified enemy targets cannot repeat. Unspecified targets
    are not fabricated or treated as enemy models.
    """
    if not isinstance(declarations, tuple) or not all(
        isinstance(d, CastDeclaration) for d in declarations
    ):
        raise TypeError("declarations must be a tuple of CastDeclaration")
    if not isinstance(caster_profile_id, str) or not caster_profile_id.strip():
        raise ValueError("caster_profile_id must be non-empty")
    if not isinstance(active_army_rule_ids, frozenset) or not all(
        isinstance(x, str) for x in active_army_rule_ids
    ):
        raise TypeError("active_army_rule_ids must be a frozenset of strings")
    enhanced = (
        caster_profile_id == NECROMANCER_PROFILE_ID
        and POWER_RULE_ID in active_army_rule_ids
    )
    if len(declarations) > (2 if enhanced else 1):
        raise ValueError("casting attempts exceed the activation limit")
    if enhanced and len({d.spell_id for d in declarations}) != len(declarations):
        raise ValueError("the Necromancer cannot cast the same power twice")
    enemy_ids = [
        d.target_model_id for d in declarations if d.target_is_enemy
    ]
    if enhanced and len(enemy_ids) != len(set(enemy_ids)):
        raise ValueError("the Necromancer cannot target the same enemy twice")
