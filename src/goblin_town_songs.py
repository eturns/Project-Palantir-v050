"""DEV-078-GT-B1: I Feel a Song Coming On — command sequencing.

Author: Edward Turns (Project Lead)
Pure immutable state; no inferred battlefield positions or scoring changes.
"""
from dataclasses import dataclass
from enum import Enum

ARMY_LIST_ID = "GOBLIN_TOWN"
RULE_ID = "GT_I_FEEL_A_SONG_COMING_ON"
KING_PROFILE_ID = "GT_KING"


class Song(str, Enum):
    BATTER_AND_BEAT = "BATTER_AND_BEAT"
    YAMMER_AND_YELP = "YAMMER_AND_YELP"
    ABOMINATIONS = "ABOMINATIONS"
    BONES_WILL_BE_SHATTERED = "BONES_WILL_BE_SHATTERED"


@dataclass(frozen=True)
class SongState:
    turn: int = 1
    active_song: Song | None = None
    last_sung_song: Song | None = None
    last_sung_turn: int | None = None

    def __post_init__(self) -> None:
        if type(self.turn) is not int or self.turn < 1:
            raise ValueError("Turn must be a positive integer")
        if self.active_song is not None and not isinstance(self.active_song, Song):
            raise TypeError("Active song must be a Song")
        if self.last_sung_song is not None and not isinstance(self.last_sung_song, Song):
            raise TypeError("Last song must be a Song")
        if (self.last_sung_song is None) != (self.last_sung_turn is None):
            raise ValueError("Last song and its turn must be recorded together")
        if self.last_sung_turn is not None and (
            type(self.last_sung_turn) is not int
            or not 1 <= self.last_sung_turn <= self.turn
        ):
            raise ValueError("Invalid last sung turn")
        if self.active_song is not None and (
            self.last_sung_turn != self.turn or self.last_sung_song != self.active_song
        ):
            raise ValueError("Active song must have been sung this turn")


@dataclass(frozen=True)
class SongCommand:
    army_list_id: str
    active_army_rule_ids: tuple[str, ...]
    king_alive: bool
    king_on_battlefield: bool
    priority_determined: bool
    selected_song: Song | None = None

    def __post_init__(self) -> None:
        if type(self.army_list_id) is not str:
            raise TypeError("Army list ID must be a string")
        if not isinstance(self.active_army_rule_ids, tuple) or not all(
            type(rule) is str for rule in self.active_army_rule_ids
        ):
            raise TypeError("Active rule IDs must be a tuple of strings")
        for name in ("king_alive", "king_on_battlefield", "priority_determined"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")
        if self.selected_song is not None and not isinstance(self.selected_song, Song):
            raise TypeError("Selected song must be Song or None")


@dataclass(frozen=True)
class SongOutcome:
    state: SongState
    status: str
    sung: bool


def sing_song(state: SongState, command: SongCommand) -> SongOutcome:
    """Choose at most one song after Priority; no same-song consecutive turns.

    Caller verifies the imported king identity and ownership in GT-B3.
    """
    if not isinstance(state, SongState):
        raise TypeError("SongState required")
    if not isinstance(command, SongCommand):
        raise TypeError("SongCommand required")
    if command.army_list_id != ARMY_LIST_ID:
        raise ValueError("Goblin-town army required")
    if RULE_ID not in command.active_army_rule_ids:
        return SongOutcome(state, "rule_inactive", False)
    if command.selected_song is None:
        return SongOutcome(state, "not_declared", False)
    if state.last_sung_turn == state.turn:
        return SongOutcome(state, "already_sung_this_turn", False)
    if not command.priority_determined:
        return SongOutcome(state, "priority_not_determined", False)
    if not command.king_alive:
        return SongOutcome(state, "king_dead", False)
    if not command.king_on_battlefield:
        return SongOutcome(state, "king_absent", False)
    if state.last_sung_turn == state.turn - 1 and state.last_sung_song == command.selected_song:
        return SongOutcome(state, "same_song_as_previous_turn", False)
    updated = SongState(
        turn=state.turn,
        active_song=command.selected_song,
        last_sung_song=command.selected_song,
        last_sung_turn=state.turn,
    )
    return SongOutcome(updated, "sung", True)


def end_phase(state: SongState) -> SongState:
    if not isinstance(state, SongState):
        raise TypeError("SongState required")
    return SongState(state.turn, None, state.last_sung_song, state.last_sung_turn)


def next_turn(state: SongState) -> SongState:
    if not isinstance(state, SongState):
        raise TypeError("SongState required")
    return SongState(state.turn + 1, None, state.last_sung_song, state.last_sung_turn)


def is_song_active(state: SongState, song: Song) -> bool:
    if not isinstance(state, SongState) or not isinstance(song, Song):
        raise TypeError("SongState and Song required")
    return state.active_song == song
