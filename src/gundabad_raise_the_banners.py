"""DEV-078-AoG-E1: Raise the Banners command sequencing.

Author: Edward Turns (Project Lead)
Standalone, immutable state. No combat or scoring side effects.
"""
from dataclasses import dataclass
from enum import Enum

ARMY_LIST_ID = "GUNDABAD"
RULE_ID = "GUNDABAD_RAISE_THE_BANNERS"


class Banner(str, Enum):
    DOL_GULDUR = "DOL_GULDUR"
    GUNDABAD = "GUNDABAD"
    ANGMAR = "ANGMAR"


@dataclass(frozen=True)
class BannerState:
    turn: int = 1
    active_banner: Banner | None = None
    last_raised_banner: Banner | None = None
    last_raised_turn: int | None = None

    def __post_init__(self):
        if type(self.turn) is not int or self.turn < 1:
            raise ValueError("Turn must be a positive integer")
        if self.active_banner is not None and not isinstance(self.active_banner, Banner):
            raise TypeError("Active banner must be a Banner")
        if self.last_raised_banner is not None and not isinstance(self.last_raised_banner, Banner):
            raise TypeError("Previous banner must be a Banner")
        if (self.last_raised_turn is None) != (self.last_raised_banner is None):
            raise ValueError("Previous banner and turn must be recorded together")
        if self.last_raised_turn is not None and (
            type(self.last_raised_turn) is not int
            or not 1 <= self.last_raised_turn <= self.turn
        ):
            raise ValueError("Invalid previous banner turn")
        if self.active_banner is not None and (
            self.last_raised_turn != self.turn
            or self.active_banner != self.last_raised_banner
        ):
            raise ValueError("Active banner must be this turn's last raised banner")


@dataclass(frozen=True)
class BannerCommand:
    army_list_id: str
    active_army_rule_ids: tuple[str, ...]
    general_alive: bool
    general_on_battlefield: bool
    priority_determined: bool
    selected_banner: Banner | None = None


@dataclass(frozen=True)
class BannerOutcome:
    state: BannerState
    status: str
    raised: bool


def raise_banner(state: BannerState, command: BannerCommand) -> BannerOutcome:
    if not isinstance(state, BannerState):
        raise TypeError("BannerState required")
    if not isinstance(command, BannerCommand):
        raise TypeError("BannerCommand required")
    if command.army_list_id != ARMY_LIST_ID:
        raise ValueError("Army of Gundabad required")
    if not isinstance(command.active_army_rule_ids, tuple):
        raise TypeError("Army rule identifiers must be a tuple")
    if command.selected_banner is not None and not isinstance(command.selected_banner, Banner):
        raise TypeError("Selected banner must be a Banner or None")
    if RULE_ID not in command.active_army_rule_ids:
        return BannerOutcome(state, "rule_inactive", False)
    if command.selected_banner is None:
        return BannerOutcome(state, "not_declared", False)
    if state.last_raised_turn == state.turn:
        return BannerOutcome(state, "already_raised_this_turn", False)
    if not command.priority_determined:
        return BannerOutcome(state, "priority_not_determined", False)
    if not command.general_alive:
        return BannerOutcome(state, "general_dead", False)
    if not command.general_on_battlefield:
        return BannerOutcome(state, "general_absent", False)
    if (state.last_raised_turn == state.turn - 1
            and state.last_raised_banner == command.selected_banner):
        return BannerOutcome(state, "same_banner_as_previous_turn", False)
    updated = BannerState(
        turn=state.turn,
        active_banner=command.selected_banner,
        last_raised_banner=command.selected_banner,
        last_raised_turn=state.turn,
    )
    return BannerOutcome(updated, "raised", True)


def end_phase(state: BannerState) -> BannerState:
    """End Phase: effect expires; remember selection until next turn."""
    if not isinstance(state, BannerState):
        raise TypeError("BannerState required")
    return BannerState(
        turn=state.turn, active_banner=None,
        last_raised_banner=state.last_raised_banner,
        last_raised_turn=state.last_raised_turn,
    )


def next_turn(state: BannerState) -> BannerState:
    """Advance one turn; banner effects never persist into the next turn."""
    if not isinstance(state, BannerState):
        raise TypeError("BannerState required")
    return BannerState(
        turn=state.turn + 1, active_banner=None,
        last_raised_banner=state.last_raised_banner,
        last_raised_turn=state.last_raised_turn,
    )


def is_banner_active(state: BannerState, banner: Banner) -> bool:
    if not isinstance(state, BannerState) or not isinstance(banner, Banner):
        raise TypeError("BannerState and Banner required")
    return state.active_banner == banner
