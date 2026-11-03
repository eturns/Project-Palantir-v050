"""DEV-078-GT-B1 standalone song sequencing acceptance.

Author: Edward Turns (Project Lead)
"""
from dataclasses import FrozenInstanceError
import pytest
from goblin_town_songs import (
    ARMY_LIST_ID, RULE_ID, Song, SongState, SongCommand,
    sing_song, end_phase, next_turn, is_song_active,
)


def command(song=Song.BATTER_AND_BEAT, **overrides):
    options = dict(
        army_list_id=ARMY_LIST_ID, active_army_rule_ids=(RULE_ID,),
        king_alive=True, king_on_battlefield=True,
        priority_determined=True, selected_song=song,
    )
    options.update(overrides)
    return SongCommand(**options)


@pytest.mark.parametrize('song', list(Song))
def test_four_songs_may_be_selected(song):
    outcome=sing_song(SongState(), command(song))
    assert outcome.sung and outcome.status=='sung'
    assert outcome.state.active_song is song
    assert outcome.state.last_sung_turn==1


@pytest.mark.parametrize('song', list(Song))
def test_song_selection_expires_at_end_phase(song):
    state=sing_song(SongState(),command(song)).state
    expired=end_phase(state)
    assert expired.active_song is None
    assert expired.last_sung_song is song
    assert expired.last_sung_turn==1


def test_decline_is_not_a_use():
    state=SongState()
    outcome=sing_song(state,command(None))
    assert not outcome.sung and outcome.state==state
    assert outcome.status=='not_declared'


@pytest.mark.parametrize('field, expected', [
    ('king_alive','king_dead'),('king_on_battlefield','king_absent'),
    ('priority_determined','priority_not_determined'),
])
def test_eligibility_required(field,expected):
    outcome=sing_song(SongState(),command(**{field:False}))
    assert not outcome.sung and outcome.status==expected
    assert outcome.state==SongState()


def test_wrong_army_rejected():
    with pytest.raises(ValueError):
        sing_song(SongState(),command(army_list_id='GUNDABAD'))


def test_inactive_rule_not_activated():
    outcome=sing_song(SongState(),command(active_army_rule_ids=()))
    assert not outcome.sung and outcome.status=='rule_inactive'


def test_only_one_song_each_turn():
    state=sing_song(SongState(),command()).state
    result=sing_song(state,command(Song.YAMMER_AND_YELP))
    assert not result.sung and result.status=='already_sung_this_turn'
    assert result.state==state


@pytest.mark.parametrize('song',list(Song))
def test_cannot_repeat_same_song_next_turn(song):
    state=next_turn(end_phase(sing_song(SongState(),command(song)).state))
    outcome=sing_song(state,command(song))
    assert not outcome.sung and outcome.status=='same_song_as_previous_turn'
    assert outcome.state==state


@pytest.mark.parametrize('song',list(Song))
def test_can_switch_song_next_turn(song):
    other=next(s for s in Song if s!=song)
    state=next_turn(end_phase(sing_song(SongState(),command(song)).state))
    assert sing_song(state,command(other)).sung


def test_previous_song_can_be_used_after_a_gap_turn():
    state=sing_song(SongState(),command()).state
    state=next_turn(end_phase(state))
    state=next_turn(end_phase(state))
    assert sing_song(state,command()).sung


def test_previous_song_can_be_used_after_an_alternate_song():
    state=sing_song(SongState(),command()).state
    state=next_turn(end_phase(state))
    state=sing_song(state,command(Song.ABOMINATIONS)).state
    state=next_turn(end_phase(state))
    assert sing_song(state,command()).sung


def test_next_turn_clears_active_song_even_without_end_phase():
    state=sing_song(SongState(),command()).state
    assert next_turn(state).active_song is None


def test_active_song_lookup():
    state=sing_song(SongState(),command()).state
    assert is_song_active(state,Song.BATTER_AND_BEAT)
    assert not is_song_active(state,Song.YAMMER_AND_YELP)
    assert not is_song_active(end_phase(state),Song.BATTER_AND_BEAT)


@pytest.mark.parametrize('kwargs',[
    {'turn':0},{'turn':True},{'active_song':'BAD'},
    {'last_sung_song':Song.ABOMINATIONS},
    {'last_sung_turn':1},
    {'last_sung_song':Song.BATTER_AND_BEAT,'last_sung_turn':2},
    {'active_song':Song.BATTER_AND_BEAT},
    {'active_song':Song.BATTER_AND_BEAT,'last_sung_song':Song.YAMMER_AND_YELP,'last_sung_turn':1},
])
def test_invalid_state(kwargs):
    with pytest.raises((ValueError,TypeError)):
        SongState(**kwargs)


@pytest.mark.parametrize('field,bad',[
    ('king_alive',1),('king_on_battlefield',None),('priority_determined','yes'),
    ('active_army_rule_ids',[]),('active_army_rule_ids',('x',3)),
    ('selected_song','BATTER_AND_BEAT'),('army_list_id',None),
])
def test_invalid_command(field,bad):
    with pytest.raises(TypeError):
        command(**{field:bad})


def test_state_is_frozen():
    with pytest.raises(FrozenInstanceError):
        SongState().turn=7


@pytest.mark.parametrize('func,params',[
    (sing_song,(object(),command())),
    (sing_song,(SongState(),object())),
    (end_phase,(object(),)),
    (next_turn,(object(),)),
    (is_song_active,(object(),Song.BATTER_AND_BEAT)),
    (is_song_active,(SongState(),'song')),
])
def test_invalid_api_types(func,params):
    with pytest.raises(TypeError):
        func(*params)
