"""DEV-078-AoG-E1 standalone tests. Author: Edward Turns (Project Lead)."""
from dataclasses import replace
import pytest
from gundabad_raise_the_banners import (
    RULE_ID, Banner, BannerState, BannerCommand, raise_banner,
    end_phase, next_turn, is_banner_active,
)


def cmd(**overrides):
    values = dict(army_list_id="GUNDABAD",
                  active_army_rule_ids=(RULE_ID,),
                  general_alive=True,
                  general_on_battlefield=True,
                  priority_determined=True,
                  selected_banner=Banner.DOL_GULDUR)
    values.update(overrides)
    return BannerCommand(**values)


@pytest.mark.parametrize("banner", list(Banner))
def test_each_banner_can_be_raised(banner):
    result=raise_banner(BannerState(),cmd(selected_banner=banner))
    assert result.raised and result.status == "raised"
    assert is_banner_active(result.state,banner)


@pytest.mark.parametrize("banner", list(Banner))
def test_each_banner_expires_at_end_phase(banner):
    state=raise_banner(BannerState(),cmd(selected_banner=banner)).state
    finished=end_phase(state)
    assert finished.active_banner is None
    assert finished.last_raised_banner == banner
    assert finished.last_raised_turn == 1


@pytest.mark.parametrize("banner", list(Banner))
def test_each_banner_cannot_repeat_next_turn(banner):
    state=next_turn(end_phase(raise_banner(BannerState(),cmd(selected_banner=banner)).state))
    result=raise_banner(state,cmd(selected_banner=banner))
    assert not result.raised
    assert result.status == "same_banner_as_previous_turn"


@pytest.mark.parametrize("banner", list(Banner))
def test_each_banner_allowed_after_skipped_turn(banner):
    used=raise_banner(BannerState(),cmd(selected_banner=banner)).state
    state=next_turn(next_turn(end_phase(used)))
    assert raise_banner(state,cmd(selected_banner=banner)).raised


@pytest.mark.parametrize("banner", list(Banner))
def test_different_banner_allowed_next_turn(banner):
    previous=next_turn(end_phase(raise_banner(BannerState(),cmd()).state))
    if banner is not Banner.DOL_GULDUR:
        assert raise_banner(previous,cmd(selected_banner=banner)).raised


@pytest.mark.parametrize("key,status",[
    ("general_alive","general_dead"),
    ("general_on_battlefield","general_absent"),
    ("priority_determined","priority_not_determined"),
])
def test_activation_prerequisites(key,status):
    r=raise_banner(BannerState(),cmd(**{key:False}))
    assert not r.raised and r.status==status and r.state==BannerState()


def test_not_declared():
    assert raise_banner(BannerState(),cmd(selected_banner=None)).status=="not_declared"


def test_inactive_rule():
    assert raise_banner(BannerState(),cmd(active_army_rule_ids=())).status=="rule_inactive"


def test_wrong_army_rejected():
    with pytest.raises(ValueError,match="Gundabad"):
        raise_banner(BannerState(),cmd(army_list_id="DG_PITS"))


def test_same_turn_second_banner_blocked():
    state=raise_banner(BannerState(),cmd()).state
    result=raise_banner(state,cmd(selected_banner=Banner.ANGMAR))
    assert result.status=="already_raised_this_turn"


def test_same_turn_second_banner_blocked_after_end_phase():
    state=end_phase(raise_banner(BannerState(),cmd()).state)
    assert not raise_banner(state,cmd(selected_banner=Banner.GUNDABAD)).raised


def test_can_alternate_banners():
    first=raise_banner(BannerState(),cmd()).state
    second=raise_banner(next_turn(first),cmd(selected_banner=Banner.ANGMAR)).state
    third=raise_banner(next_turn(second),cmd()).state
    assert third.active_banner==Banner.DOL_GULDUR


def test_turn_transition_clears_active_banner():
    state=raise_banner(BannerState(),cmd()).state
    assert next_turn(state).active_banner is None


def test_does_not_modify_prior_state():
    previous=BannerState()
    raise_banner(previous,cmd())
    assert previous.active_banner is None


@pytest.mark.parametrize("value",[0,-1,1.5,True])
def test_invalid_turn_rejected(value):
    with pytest.raises(ValueError):
        BannerState(turn=value)


def test_invalid_banner_rejected():
    with pytest.raises(TypeError):
        raise_banner(BannerState(),cmd(selected_banner="ANGMAR"))


def test_inconsistent_state_rejected():
    with pytest.raises(ValueError):
        BannerState(active_banner=Banner.ANGMAR)


def test_already_raised_same_banner_cannot_repeat_this_turn():
    state=raise_banner(BannerState(),cmd()).state
    assert not raise_banner(state,cmd()).raised
