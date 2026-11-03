"""DEV-078-GT-B2 — four Goblin King song effects.

Author: Edward Turns (Project Lead)
Standalone battlefield evidence only. No position inference, scoring or roster mutation.
"""
from dataclasses import dataclass, replace
from fractions import Fraction
from math import isfinite

from goblin_town_songs import Song, SongState, is_song_active, KING_PROFILE_ID


@dataclass(frozen=True)
class SongTarget:
    """Explicit, caller-verified battlefield evidence about ONE target model."""
    profile_id: str
    friendly_to_king: bool
    goblin_faction: bool
    distance_to_king_inches: float

    def __post_init__(self):
        if not isinstance(self.profile_id, str) or not self.profile_id:
            raise ValueError("Profile ID required")
        for name in ("friendly_to_king", "goblin_faction"):
            if type(getattr(self, name)) is not bool:
                raise TypeError(f"{name} must be bool")
        d = self.distance_to_king_inches
        if type(d) not in (int, float) or not isfinite(d) or d < 0:
            raise ValueError("Distance must be finite and nonnegative")


def affected(state: SongState, song: Song, target: SongTarget) -> bool:
    if not isinstance(target, SongTarget):
        raise TypeError("SongTarget required")
    return (is_song_active(state, song)
            and target.friendly_to_king and target.goblin_faction
            and target.profile_id != KING_PROFILE_ID
            and target.distance_to_king_inches <= 6.0)


def has_song_banner_support(state: SongState, target: SongTarget) -> bool:
    """Batter and beat: target treats King as a 6-inch banner."""
    return affected(state, Song.BATTER_AND_BEAT, target)


def apply_song_banner_to_side(side, state: SongState, targets: tuple[SongTarget, ...]):
    """Preserve the normal combat-side banner reroll and all existing fields."""
    from combat_side import CombatSide
    if not isinstance(side, CombatSide):
        raise TypeError("CombatSide required")
    if not isinstance(targets, tuple):
        raise TypeError("Tuple of SongTarget required")
    support = any(has_song_banner_support(state, t) for t in targets)
    return replace(side, reroll_available=side.reroll_available or support)


def causes_song_terror(state: SongState, target: SongTarget) -> bool:
    """Yammer and yelp: target causes Terror for this turn."""
    return affected(state, Song.YAMMER_AND_YELP, target)


def song_wound_prevention_probability(state: SongState, target: SongTarget) -> Fraction:
    """Abominations: one natural-six prevention roll per suffered Wound."""
    return Fraction(1, 6) if affected(state, Song.ABOMINATIONS, target) else Fraction(0)


def resolve_song_wound_prevention(state: SongState, target: SongTarget, natural_d6: int) -> bool:
    if type(natural_d6) is not int or not 1 <= natural_d6 <= 6:
        raise ValueError("Natural wound-prevention roll must be 1..6")
    return bool(song_wound_prevention_probability(state, target)) and natural_d6 == 6


def song_wound_reroll_eligible(
    state: SongState, target: SongTarget, *, making_strikes: bool
) -> bool:
    """Bones: reroll natural ones To Wound, only when making Strikes."""
    if type(making_strikes) is not bool:
        raise TypeError("making_strikes must be bool")
    return making_strikes and affected(state, Song.BONES_WILL_BE_SHATTERED, target)


def with_song_strike_wound_reroll(
    existing, state: SongState, target: SongTarget, *, making_strikes: bool
):
    """Merge entitlement with the engine's WoundReroll contract.

    Does not create an extra reroll when one already exists.
    """
    from wound_reroll import WoundReroll
    if not isinstance(existing, WoundReroll):
        raise TypeError("WoundReroll required")
    return WoundReroll(
        reroll_failed=existing.reroll_failed,
        reroll_natural_ones=(existing.reroll_natural_ones
                            or song_wound_reroll_eligible(
                                state, target, making_strikes=making_strikes)),
    )
