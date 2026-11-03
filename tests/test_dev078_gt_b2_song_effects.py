"""DEV-078-GT-B2 standalone acceptance.

Author: Edward Turns (Project Lead)
"""
from dataclasses import replace
from fractions import Fraction
import pytest

from goblin_town_songs import Song, SongState, end_phase, next_turn
from goblin_town_song_effects import (
    SongTarget, affected, has_song_banner_support, causes_song_terror,
    song_wound_prevention_probability, resolve_song_wound_prevention,
    song_wound_reroll_eligible, with_song_strike_wound_reroll,
)
from wound_reroll import WoundReroll


def active(song):
    return SongState(turn=1, active_song=song, last_sung_song=song, last_sung_turn=1)


def target(**kwargs):
    return replace(SongTarget("GT_WARRIOR", True, True, 4.0), **kwargs)


@pytest.mark.parametrize("song", list(Song))
def test_matching_song_affects_eligible_goblin(song):
    assert affected(active(song),song,target())


@pytest.mark.parametrize("song",list(Song))
def test_inactive_song_has_no_effect(song):
    assert not affected(SongState(),song,target())


@pytest.mark.parametrize("song",list(Song))
@pytest.mark.parametrize("change",[
    {"profile_id":"GT_KING"},
    {"friendly_to_king":False},
    {"goblin_faction":False},
    {"distance_to_king_inches":6.01},
])
def test_excluded_targets(song,change):
    assert not affected(active(song),song,target(**change))


@pytest.mark.parametrize("song", list(Song))
@pytest.mark.parametrize("distance",[0,3,6])
def test_song_radius_inclusive(song,distance):
    assert affected(active(song),song,target(distance_to_king_inches=distance))


@pytest.mark.parametrize("song",list(Song))
def test_expired_at_end_phase(song):
    assert not affected(end_phase(active(song)),song,target())


@pytest.mark.parametrize("song",list(Song))
def test_expired_on_new_turn(song):
    assert not affected(next_turn(active(song)),song,target())


def test_banner_only_correct_song():
    assert has_song_banner_support(active(Song.BATTER_AND_BEAT),target())
    assert not has_song_banner_support(active(Song.YAMMER_AND_YELP),target())


def test_terror_only_correct_song():
    assert causes_song_terror(active(Song.YAMMER_AND_YELP),target())
    assert not causes_song_terror(active(Song.ABOMINATIONS),target())


def test_wound_prevention_natural_six_only():
    s=active(Song.ABOMINATIONS)
    assert song_wound_prevention_probability(s,target()) == Fraction(1,6)
    for d in range(1,7):
        assert resolve_song_wound_prevention(s,target(),d) is (d==6)


def test_wound_prevention_no_other_song():
    assert song_wound_prevention_probability(active(Song.BATTER_AND_BEAT),target())==0


@pytest.mark.parametrize("bad",[0,7,True,4.5,"6"])
def test_invalid_roll(bad):
    with pytest.raises(ValueError):
        resolve_song_wound_prevention(active(Song.ABOMINATIONS),target(),bad)


def test_strike_only_reroll_ones():
    s=active(Song.BONES_WILL_BE_SHATTERED)
    assert song_wound_reroll_eligible(s,target(),making_strikes=True)
    assert not song_wound_reroll_eligible(s,target(),making_strikes=False)


def test_reroll_merged_with_existing_failed_rerolls():
    s=active(Song.BONES_WILL_BE_SHATTERED)
    result=with_song_strike_wound_reroll(WoundReroll(reroll_failed=True),s,target(),making_strikes=True)
    assert result.reroll_failed and result.reroll_natural_ones


def test_reroll_does_not_activate_shooting():
    s=active(Song.BONES_WILL_BE_SHATTERED)
    result=with_song_strike_wound_reroll(WoundReroll(),s,target(),making_strikes=False)
    assert result==WoundReroll()


def test_reroll_preserves_existing_reroll_ones():
    result=with_song_strike_wound_reroll(WoundReroll(reroll_natural_ones=True),
                                         SongState(),target(),making_strikes=True)
    assert result.reroll_natural_ones


@pytest.mark.parametrize("bad",[-1,float("nan"),float("inf"),"3",True])
def test_bad_distances_rejected(bad):
    with pytest.raises((ValueError,TypeError)):
        target(distance_to_king_inches=bad)


@pytest.mark.parametrize("field",["friendly_to_king","goblin_faction"])
def test_boolean_type_rejected(field):
    with pytest.raises(TypeError):
        target(**{field:1})


def test_nonboolean_strikes_rejected():
    with pytest.raises(TypeError):
        song_wound_reroll_eligible(active(Song.BONES_WILL_BE_SHATTERED),target(),making_strikes=1)


def test_non_song_target_rejected():
    with pytest.raises(TypeError):
        affected(active(Song.BATTER_AND_BEAT),Song.BATTER_AND_BEAT,object())
