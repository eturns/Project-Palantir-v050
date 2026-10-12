"""Generic, non-scoring pre-move reposition validation for MESBG.

The caller supplies measured model-centre coordinates and adjudicates physical
placement legality (terrain, base overlap, board edge, line of sight, etc.).
This module never treats a displacement as ordinary Movement.
"""
from dataclasses import dataclass, field
from enum import Enum
from math import dist, isfinite


class RepositionKind(Enum):
    SELF = "self"
    ALLY_ANCHOR = "ally_anchor"


class RepositionTiming(Enum):
    PRE_HEROIC_ACTIONS = "pre_heroic_actions"
    OTHER = "other"


@dataclass(frozen=True)
class RepositionRule:
    kind: RepositionKind
    radius_inches: float
    usage_group: str
    once_per_turn: bool = True
    does_not_count_as_moving: bool = True

    def __post_init__(self):
        if not isfinite(self.radius_inches) or self.radius_inches < 0:
            raise ValueError("Reposition radius must be finite and non-negative")
        if not self.usage_group:
            raise ValueError("usage_group cannot be empty")


@dataclass(frozen=True)
class RepositionRequest:
    actor_id: str
    origin: tuple[float, float]
    destination: tuple[float, float]
    timing: RepositionTiming
    anchor_id: str | None = None
    anchor_position: tuple[float, float] | None = None
    anchor_is_eligible: bool = False
    actor_on_board: bool = True
    anchor_on_board: bool = True
    legal_placement: bool = True
    in_enemy_base_contact: bool = False


@dataclass
class RepositionUsage:
    """Tracks activated groups per turn; create one state per game."""
    turn: int | None = None
    used_groups: set[str] = field(default_factory=set)

    def begin_turn(self, turn: int) -> None:
        if turn < 1:
            raise ValueError("Turn must be positive")
        if self.turn is not None and turn < self.turn:
            raise ValueError("Cannot rewind reposition turn state")
        if self.turn != turn:
            self.turn = turn
            self.used_groups.clear()


def _valid_position(position: tuple[float, float]) -> bool:
    return (
        isinstance(position, tuple)
        and len(position) == 2
        and all(isinstance(v, (float, int)) and not isinstance(v, bool) and isfinite(v) for v in position)
    )


def validate_reposition(
    rule: RepositionRule,
    request: RepositionRequest,
    usage: RepositionUsage,
) -> tuple[bool, str]:
    """Pure validation. Call apply_reposition only after validation succeeds."""
    if usage.turn is None:
        return False, "Turn has not started"
    if request.timing is not RepositionTiming.PRE_HEROIC_ACTIONS:
        return False, "Reposition must occur before Heroic Actions"
    if not request.actor_on_board:
        return False, "Actor is not on the battlefield"
    if not request.legal_placement or request.in_enemy_base_contact:
        return False, "Destination is not a legal non-contact placement"
    if rule.once_per_turn and rule.usage_group in usage.used_groups:
        return False, "Reposition usage already spent this turn"
    if not _valid_position(request.origin) or not _valid_position(request.destination):
        return False, "Invalid position"

    reference = request.origin
    if rule.kind is RepositionKind.ALLY_ANCHOR:
        if (
            not request.anchor_id
            or request.anchor_id == request.actor_id
            or not request.anchor_is_eligible
            or not request.anchor_on_board
            or not _valid_position(request.anchor_position)
        ):
            return False, "Eligible distinct anchor on board required"
        reference = request.anchor_position

    if dist(reference, request.destination) > rule.radius_inches + 1e-9:
        return False, "Destination exceeds reposition radius"
    return True, "Valid reposition"


def apply_reposition(
    rule: RepositionRule,
    request: RepositionRequest,
    usage: RepositionUsage,
) -> None:
    valid, reason = validate_reposition(rule, request, usage)
    if not valid:
        raise ValueError(reason)
    if rule.once_per_turn:
        usage.used_groups.add(rule.usage_group)


def unnatural_speed_rule(model_id: str) -> RepositionRule:
    """Lingering Shadow: independent 3-inch displacement, once each turn."""
    return RepositionRule(RepositionKind.SELF, 3.0, f"self-reposition:{model_id}")


def spiritual_displacement_rule() -> RepositionRule:
    """Abyssal Knights: only one of the pair can displace each turn."""
    return RepositionRule(RepositionKind.ALLY_ANCHOR, 3.0, "abyssal-knights:spiritual-displacement")
