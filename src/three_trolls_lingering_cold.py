"""DEV-077-TT-D2C: Tom's Lingering Cold, an explicit combat-state resolver.

Source: MESBG Armies of the Hobbit (2024), Tom the Troll, p. 142.
No existing Palantir combat scoring is changed by this module.
"""
from dataclasses import dataclass
from fractions import Fraction

TOM_PROFILE_ID = "TT_TOM"
RULE_ID = "LINGERING_COLD"


@dataclass(frozen=True)
class LingeringColdContext:
    actor_profile_id: str
    actor_will_available: int
    at_start_of_combat: bool
    engaged_enemy_ids: tuple[str, ...]
    target_id: str
    target_fight: int
    actor_can_use_rule: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.actor_will_available, int) or isinstance(self.actor_will_available, bool) or self.actor_will_available < 0:
            raise ValueError("Available Will must be a non-negative integer")
        if not isinstance(self.target_fight, int) or isinstance(self.target_fight, bool) or self.target_fight < 0:
            raise ValueError("Target Fight must be a non-negative integer")
        if not self.target_id:
            raise ValueError("Target ID must be provided")
        if len(self.engaged_enemy_ids) != len(set(self.engaged_enemy_ids)):
            raise ValueError("Engaged enemy IDs must be unique")


@dataclass(frozen=True)
class LingeringColdResult:
    used: bool
    will_spent: int
    remaining_will: int
    affected_target_id: str | None
    original_fight: int
    halved_fight_exact: Fraction | None
    expires: str | None
    reason: str | None


def resolve_lingering_cold(context: LingeringColdContext, *, activate: bool = True) -> LingeringColdResult:
    """Resolve eligibility and resource expenditure without mutating game state.

    The exact half is retained as a Fraction rather than silently choosing
    an unsupported rounding policy. Combat integration must apply the
    appropriate Rules Manual rounding convention explicitly.
    """
    reason = None
    if not activate:
        reason = "not_selected"
    elif context.actor_profile_id != TOM_PROFILE_ID:
        reason = "wrong_profile"
    elif not context.actor_can_use_rule:
        reason = "rule_unavailable"
    elif not context.at_start_of_combat:
        reason = "wrong_timing"
    elif context.actor_will_available < 1:
        reason = "insufficient_will"
    elif context.target_id not in context.engaged_enemy_ids:
        reason = "target_not_engaged"
    if reason:
        return LingeringColdResult(False, 0, context.actor_will_available, None, context.target_fight, None, None, reason)
    return LingeringColdResult(True, 1, context.actor_will_available - 1, context.target_id, context.target_fight, Fraction(context.target_fight, 2), "end_of_turn", None)
