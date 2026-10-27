"""DEV-077-TT-D4D: Tasty Livestock, Cover of Darkness, and Stash markers.

Rules authority: MESBG Armies of the Hobbit (2024), page 158.
Pure purchase-gated diagnostics; positions and turn events must be supplied.
No combat scores, objective scores, or army state are mutated.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, hypot
from three_trolls_d4a_effects import _ensure_hoard, _ensure_troll
from three_trolls_hoard import HoardEvidence

LIVESTOCK_COUNT = 4
MARKER_BASE_MM = 25
LIVESTOCK_HEAL_RANGE = 3.0
LIVESTOCK_ENEMY_OBJECTIVE_EXCLUSION = 3.0
LIVESTOCK_EDGE_MARKER_EXCLUSION = 6.0


def _position(value, field="position"):
    if not isinstance(value, (tuple, list)) or len(value) != 2 or any(
        type(v) not in (int, float) or not isfinite(v) for v in value
    ):
        raise ValueError(f"{field} must be a finite (x, y) pair in inches")
    return tuple(float(v) for v in value)


def _distance(a, b):
    return hypot(a[0] - b[0], a[1] - b[1])


def _distance_to_rect_edge(pt, width, height):
    return min(pt[0], pt[1], width - pt[0], height - pt[1])


@dataclass(frozen=True)
class LivestockPlacementEvidence:
    purchased: bool
    allowed: bool
    reason: str
    marker_base_mm: int = MARKER_BASE_MM


def validate_livestock_placement(
    hoard: HoardEvidence,
    *,
    proposed_position,
    board_width_inches: float,
    board_height_inches: float,
    enemy_positions=(),
    objective_positions=(),
    existing_livestock_positions=(),
    after_both_deployed: bool,
    before_first_turn: bool,
) -> LivestockPlacementEvidence:
    """Centre-point distance contract; the caller supplies battlefield positions.

    Rules prohibit setup WITHIN 3in of enemy/objective, and WITHIN 6in of
    board edge/other marker: exactly 3in or 6in is permitted.
    """
    _ensure_hoard(hoard)
    purchased = hoard.has("Tasty Livestock")
    if not purchased:
        return LivestockPlacementEvidence(False, False, "not_purchased")
    if type(after_both_deployed) is not bool or type(before_first_turn) is not bool:
        raise TypeError("Deployment timing flags must be boolean")
    if not after_both_deployed or not before_first_turn:
        return LivestockPlacementEvidence(True, False, "outside_placement_window")
    if any(type(n) not in (int, float) or not isfinite(n) or n <= 0
           for n in (board_width_inches, board_height_inches)):
        raise ValueError("Board dimensions must be finite and positive")
    pos = _position(proposed_position)
    enemy = tuple(_position(x) for x in enemy_positions)
    objectives = tuple(_position(x) for x in objective_positions)
    livestock = tuple(_position(x) for x in existing_livestock_positions)
    if len(livestock) >= LIVESTOCK_COUNT:
        return LivestockPlacementEvidence(True, False, "four_markers_already_placed")
    if not 0 <= pos[0] <= board_width_inches or not 0 <= pos[1] <= board_height_inches:
        return LivestockPlacementEvidence(True, False, "outside_board")
    if _distance_to_rect_edge(pos, board_width_inches, board_height_inches) < 6:
        return LivestockPlacementEvidence(True, False, "too_close_to_edge")
    if any(_distance(pos, x) < 3 for x in (*enemy, *objectives)):
        return LivestockPlacementEvidence(True, False, "too_close_to_enemy_or_objective")
    if any(_distance(pos, x) < 6 for x in livestock):
        return LivestockPlacementEvidence(True, False, "too_close_to_livestock")
    return LivestockPlacementEvidence(True, True, "legal")


@dataclass(frozen=True)
class LivestockHealingEvidence:
    purchased: bool
    eligible: bool
    wounds_restored: int
    marker_removed: bool
    reason: str


def consume_livestock(
    hoard: HoardEvidence, profile_id: str, *,
    distance_inches: float,
    during_own_activation: bool,
    friendly_marker_present: bool,
    wounds_lost: int,
) -> LivestockHealingEvidence:
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    if type(distance_inches) not in (int, float) or not isfinite(distance_inches) or distance_inches < 0:
        raise ValueError("distance must be nonnegative and finite")
    if type(wounds_lost) is not int or wounds_lost < 0:
        raise ValueError("wounds_lost must be a nonnegative integer")
    if type(during_own_activation) is not bool or type(friendly_marker_present) is not bool:
        raise TypeError("Activation/marker flags must be boolean")
    purchased = hoard.has("Tasty Livestock")
    reason = (
        "not_purchased" if not purchased else
        "not_own_activation" if not during_own_activation else
        "no_friendly_marker" if not friendly_marker_present else
        "out_of_range" if distance_inches > 3 else
        "eligible"
    )
    eligible = reason == "eligible"
    return LivestockHealingEvidence(
        purchased, eligible, 1 if eligible and wounds_lost > 0 else 0,
        eligible, reason,
    )


@dataclass(frozen=True)
class CoverOfDarknessEvidence:
    purchased: bool
    may_choose_night: bool
    grants_cave_dweller: bool
    night_selected: bool | None
    status: str


def cover_of_darkness(
    hoard: HoardEvidence, profile_id: str, *,
    at_start_of_game: bool | None = None,
    select_night: bool | None = None,
) -> CoverOfDarknessEvidence:
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    if at_start_of_game is not None and type(at_start_of_game) is not bool:
        raise TypeError("at_start_of_game must be bool or None")
    if select_night is not None and type(select_night) is not bool:
        raise TypeError("select_night must be bool or None")
    purchased = hoard.has("Cover of Darkness")
    if not purchased:
        if select_night is True:
            raise ValueError("Night selection requires Cover of Darkness purchase")
        return CoverOfDarknessEvidence(False, False, False, False, "not_purchased")
    if select_night is True and at_start_of_game is not True:
        raise ValueError("Night must be chosen at the start of the game")
    return CoverOfDarknessEvidence(
        True, True, True, select_night,
        "evaluated" if at_start_of_game is True and select_night is not None else "conditional_not_evaluated",
    )


@dataclass(frozen=True)
class StashPlacementEvidence:
    purchased: bool
    allowed: bool
    reason: str
    marker_base_mm: int = MARKER_BASE_MM


def place_stash(
    hoard: HoardEvidence, profile_id: str, *,
    at_start_of_activation: bool,
    troll_has_stash: bool,
    placed_in_base_contact: bool,
) -> StashPlacementEvidence:
    _ensure_hoard(hoard)
    _ensure_troll(profile_id)
    if any(type(x) is not bool for x in (
        at_start_of_activation, troll_has_stash, placed_in_base_contact
    )):
        raise TypeError("Stash placement conditions must be boolean")
    reason = (
        "not_purchased" if not hoard.has("\"That's Mine That Is!\"") else
        "not_activation_start" if not at_start_of_activation else
        "already_has_stash" if troll_has_stash else
        "not_in_base_contact" if not placed_in_base_contact else
        "legal"
    )
    return StashPlacementEvidence(hoard.has("\"That's Mine That Is!\""), reason == "legal", reason)


@dataclass(frozen=True)
class StashObjectiveEvidence:
    purchased: bool
    friendly_warrior_equivalent: int
    status: str


def stash_objective_presence(
    hoard: HoardEvidence, *, marker_exists: bool, within_objective_range: bool | None
) -> StashObjectiveEvidence:
    _ensure_hoard(hoard)
    if type(marker_exists) is not bool or (
        within_objective_range is not None and type(within_objective_range) is not bool
    ):
        raise TypeError("Marker and objective flags must be booleans")
    purchased = hoard.has("\"That's Mine That Is!\"")
    if not purchased or not marker_exists:
        return StashObjectiveEvidence(purchased, 0, "evaluated")
    if within_objective_range is None:
        return StashObjectiveEvidence(True, 0, "conditional_not_evaluated")
    return StashObjectiveEvidence(True, int(within_objective_range), "evaluated")


@dataclass(frozen=True)
class StashRemovalEvidence:
    purchased: bool
    enemy_can_remove: bool
    reason: str


def enemy_remove_stash(
    hoard: HoardEvidence, *,
    marker_exists: bool,
    enemy_in_base_contact: bool,
    during_end_phase: bool,
    cast_magic: bool = False,
    used_missile_weapon: bool = False,
    engaged_in_combat: bool = False,
    supported_combat: bool = False,
    unable_to_move: bool = False,
    under_enemy_magic: bool = False,
) -> StashRemovalEvidence:
    _ensure_hoard(hoard)
    flags = (marker_exists, enemy_in_base_contact, during_end_phase, cast_magic,
             used_missile_weapon, engaged_in_combat, supported_combat,
             unable_to_move, under_enemy_magic)
    if any(type(x) is not bool for x in flags):
        raise TypeError("Stash removal conditions must be booleans")
    purchased = hoard.has("\"That's Mine That Is!\"")
    reason = (
        "not_purchased" if not purchased else
        "no_marker" if not marker_exists else
        "not_in_base_contact" if not enemy_in_base_contact else
        "not_end_phase" if not during_end_phase else
        "disqualified_by_turn_activity" if any(flags[3:]) else
        "legal"
    )
    return StashRemovalEvidence(purchased, reason == "legal", reason)
