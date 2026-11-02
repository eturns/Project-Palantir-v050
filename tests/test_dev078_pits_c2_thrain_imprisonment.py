"""DEV-078-PITS-C2: standalone Shattered Spirit contextual acceptance.

Author: Edward Turns (Project Lead)
"""
import pytest
from pits_thrain_imprisonment import resolve_thrain_imprisonment as resolve
from shattered_spirit_state import ShatteredSpiritResult as Result


def check(**overrides):
    args = dict(
        army_list_id="DG_PITS",
        active_army_rule_ids=("DG_THRAINS_IMPRISONMENT",),
        first_die=1, second_die=2, intelligence="6+",
        keeper_on_battlefield=True, keeper_distance_inches=6.0,
    )
    args.update(overrides)
    return resolve(**args)


def test_failed_test_within_six_becomes_normal():
    r = check()
    assert r.original_state.result is Result.OPPONENT_CONTROLLED
    assert r.effective_state.result is Result.NORMAL
    assert r.imprisonment_applied and r.thrain_counts_as_evil


def test_exactly_six_inches_is_in_range():
    assert check(keeper_distance_inches=6).imprisonment_applied


def test_outside_six_inches_preserves_failure():
    r = check(keeper_distance_inches=6.001)
    assert r.effective_state.result is Result.OPPONENT_CONTROLLED
    assert not r.imprisonment_applied


def test_keeper_absent_preserves_failure():
    r = check(keeper_on_battlefield=False, keeper_distance_inches=None)
    assert r.effective_state.result is Result.OPPONENT_CONTROLLED


def test_failed_doubles_are_not_empowered():
    r = check(first_die=2, second_die=2, intelligence="6+")
    assert r.imprisonment_applied
    assert r.effective_state.result is Result.NORMAL


def test_successful_double_preserves_empowered():
    r = check(first_die=4, second_die=4, intelligence="6+")
    assert not r.imprisonment_applied
    assert r.effective_state.result is Result.EMPOWERED


def test_successful_non_double_stays_normal():
    r = check(first_die=3, second_die=4, intelligence="6+")
    assert not r.imprisonment_applied
    assert r.effective_state.result is Result.NORMAL


def test_no_rule_preserves_intrinsic_result():
    r = check(active_army_rule_ids=())
    assert r.effective_state.result is Result.OPPONENT_CONTROLLED
    assert not r.thrain_counts_as_evil


def test_other_army_cannot_activate_rule():
    r = check(army_list_id="DG_ROTN")
    assert not r.imprisonment_applied
    assert not r.thrain_counts_as_evil


def test_no_score_generated():
    r = check()
    assert r.dashboard_score is None and r.scenario_score is None


@pytest.mark.parametrize("distance", [-1, float("inf"), float("nan"), True])
def test_invalid_distance_rejected(distance):
    with pytest.raises((ValueError, TypeError)):
        check(keeper_distance_inches=distance)


def test_keeper_position_unknown_is_not_assumed():
    with pytest.raises(ValueError, match="declared distance"):
        check(keeper_distance_inches=None)


def test_absent_keeper_cannot_have_declared_distance():
    with pytest.raises(ValueError, match="absent Keeper"):
        check(keeper_on_battlefield=False)


def test_invalid_original_roll_still_rejected():
    with pytest.raises(ValueError, match="first_die"):
        check(first_die=0)
