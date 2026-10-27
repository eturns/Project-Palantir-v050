"""DEV-077-TT-D2F: explicit action integration for the Three Trolls.

2024 authority: Armies of the Hobbit, PDF pp. 140-142.
This API consumes *observed* combat context and delegates to the tested
D2A-E resolvers. It never assumes a Duel win or changes army capability scores.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from fractions import Fraction

from three_trolls_keep_em_for_later import (
    CaptureAction, CaptureContext, CaptiveState, apply_keep_for_later,
)
from three_trolls_lingering_cold import LingeringColdContext, resolve_lingering_cold
from three_trolls_mince_em_fine import mince_em_fine_distribution
from three_trolls_roast_em_slowly import RoastEmSlowlyContext, resolve_roast_em_slowly

TROLL_IDS = frozenset(("TT_BILL", "TT_BERT", "TT_TOM"))


class TrollCombatAction(str, Enum):
    MINCE = "mince_em_fine"
    ROAST = "roast_em_slowly"
    SQUASH = "squash_em_into_jelly"
    CAPTURE = "keep_em_for_later"
    COLD = "lingering_cold"


@dataclass(frozen=True)
class TrollCombatRequest:
    profile_id: str
    actor_id: str
    action: TrollCombatAction
    won_duel: bool = False
    target_id: str | None = None
    engaged_enemies: tuple[str, ...] = ()
    # Declare chosen attack, after winning the Duel; never allow two alternatives.
    alternative_attack_already_used: bool = False
    # Supplied observations, not inferred from a profile or army.
    target_strength: int | None = None
    target_defence: int | None = None
    target_base_mm: int | None = None
    campfire_distance_inches: float | None = None
    campfire_present: bool = False
    available_will: int | None = None
    target_fight: int | None = None
    at_start_of_combat: bool = False

    def __post_init__(self) -> None:
        if self.profile_id not in TROLL_IDS:
            raise ValueError("Not a Three Trolls profile")
        if not self.actor_id:
            raise ValueError("actor_id is required")
        if not isinstance(self.action, TrollCombatAction):
            raise ValueError("action must be TrollCombatAction")
        if len(self.engaged_enemies) != len(set(self.engaged_enemies)):
            raise ValueError("engaged_enemies must be unique")


@dataclass(frozen=True)
class TrollCombatEvidence:
    action: TrollCombatAction
    status: str  # evaluated, conditional_unavailable, not_evaluated
    result: object | None = None
    expected_wounds_before_saves: Fraction | None = None
    consumes_normal_strikes: bool = False
    reason: str | None = None


def resolve_troll_combat_action(request: TrollCombatRequest) -> TrollCombatEvidence:
    """Dispatch exactly one selected action, without mutating game state.

    A battle-state caller must apply effects and resolve casualties/Fate.
    'not_evaluated' means required external context was not provided.
    """
    action = request.action
    unavailable = lambda reason: TrollCombatEvidence(action, "conditional_unavailable", reason=reason)
    incomplete = lambda reason: TrollCombatEvidence(action, "not_evaluated", reason=reason)
    if action is TrollCombatAction.COLD:
        if request.profile_id != "TT_TOM":
            return unavailable("wrong_profile")
        if request.target_id is None or request.available_will is None or request.target_fight is None:
            return incomplete("combat_target_fight_or_will_unknown")
        response = resolve_lingering_cold(LingeringColdContext(
            actor_profile_id=request.profile_id,
            actor_will_available=request.available_will,
            at_start_of_combat=request.at_start_of_combat,
            engaged_enemy_ids=request.engaged_enemies,
            target_id=request.target_id, target_fight=request.target_fight,
        ))
        return TrollCombatEvidence(action, "evaluated" if response.used else "conditional_unavailable",
                                    result=response, reason=response.reason)

    if not request.won_duel:
        return unavailable("duel_not_won")
    if request.alternative_attack_already_used:
        return unavailable("alternative_attack_already_used")
    if not request.engaged_enemies:
        return incomplete("engaged_enemies_unknown")

    if action is TrollCombatAction.MINCE:
        if request.profile_id != "TT_BILL":
            return unavailable("wrong_profile")
        if request.target_id not in request.engaged_enemies:
            return unavailable("target_not_engaged")
        if request.target_strength is None:
            return incomplete("target_strength_unknown")
        distribution = mince_em_fine_distribution(bill_strength=7, target_strength=request.target_strength)
        expected = sum((w * p for w, p in distribution.items()), Fraction())
        return TrollCombatEvidence(action, "evaluated", distribution, expected, True)

    if action is TrollCombatAction.ROAST:
        if request.profile_id != "TT_BERT":
            return unavailable("wrong_profile")
        if request.target_id not in request.engaged_enemies:
            return unavailable("target_not_engaged")
        if request.campfire_distance_inches is None and request.campfire_present:
            return incomplete("campfire_distance_unknown")
        response = resolve_roast_em_slowly(RoastEmSlowlyContext(
            attacker_profile_id=request.profile_id, target_id=request.target_id,
            attacker_won_duel=True, target_is_enemy_in_combat=True,
            campfire_present=request.campfire_present,
            campfire_distance_inches=request.campfire_distance_inches,
        ))
        if response is None:
            return unavailable("campfire_condition_not_met")
        return TrollCombatEvidence(action, "evaluated", response, consumes_normal_strikes=True)

    if action is TrollCombatAction.SQUASH:
        if request.profile_id != "TT_TOM":
            return unavailable("wrong_profile")
        if request.target_defence is None or len(request.engaged_enemies) != 1:
            return incomplete("per_target_defence_required_use_group_resolver")
        # Full multiple-target operation uses the standalone SquashContext,
        # dispatched through the next helper below.
        from three_trolls_squash_em_into_jelly import (
            SquashContext, SquashTarget, resolve_squash_em_into_jelly,
        )
        response = resolve_squash_em_into_jelly(SquashContext(
            attacker_profile_id=request.profile_id, attacker_won_duel=True,
            engaged_enemies=(SquashTarget(request.engaged_enemies[0], request.target_defence),),
        ))
        return TrollCombatEvidence(action, "evaluated", response,
                                    response.expected_wounds_before_saves, True)

    if action is TrollCombatAction.CAPTURE:
        if request.target_id not in request.engaged_enemies:
            return unavailable("target_not_engaged")
        if request.target_base_mm is None:
            return incomplete("target_base_unknown")
        if request.target_base_mm != 25:
            return unavailable("target_not_25mm")
        outcome = apply_keep_for_later(CaptureContext(
            troll_profile_id=request.profile_id, troll_model_id=request.actor_id,
            won_duel=True, action=CaptureAction.KEEP_FOR_LATER,
            target=CaptiveState(request.target_id, request.target_base_mm, True, True),
        ))
        return TrollCombatEvidence(action, "evaluated", outcome, consumes_normal_strikes=True)
    raise ValueError(f"Unhandled action {action}")


def resolve_tom_squash_group(*, actor_id: str, won_duel: bool,
                             targets: tuple[tuple[str, int], ...]):
    """All engaged enemies in one Squash attack; caller supplies each Defence."""
    from three_trolls_squash_em_into_jelly import (
        SquashContext, SquashTarget, resolve_squash_em_into_jelly,
    )
    if not actor_id:
        raise ValueError("actor_id required")
    response = resolve_squash_em_into_jelly(SquashContext(
        attacker_profile_id="TT_TOM", attacker_won_duel=won_duel,
        engaged_enemies=tuple(SquashTarget(id_, defence) for id_, defence in targets),
    ))
    return TrollCombatEvidence(
        TrollCombatAction.SQUASH,
        "evaluated" if response is not None else "conditional_unavailable",
        response,
        response.expected_wounds_before_saves if response else None,
        response is not None,
        None if response else "duel_not_won_or_no_targets",
    )
