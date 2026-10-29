import pytest
from smaug_immovable_object import resolve_immovable_object as resolve


def test_immovable_never_prone_or_forcibly_moved():
    r=resolve(has_immovable_object=True,lost_duel=False)
    assert not r.can_be_knocked_prone
    assert not r.can_be_forced_to_move


def test_lost_duel_opponent_backs_away_instead():
    r=resolve(has_immovable_object=True,lost_duel=True)
    assert not r.smaug_backs_away
    assert not r.smaug_counts_as_trapped
    assert r.opponent_must_back_away


def test_winning_duel_does_not_force_retreat():
    assert not resolve(has_immovable_object=True,lost_duel=False).opponent_must_back_away


def test_rule_absent_never_grants_smaug_override():
    r=resolve(has_immovable_object=False,lost_duel=True)
    assert r.can_be_knocked_prone and r.can_be_forced_to_move
    assert not r.opponent_must_back_away


def test_rule_requires_explicit_facts():
    with pytest.raises(TypeError):
        resolve(has_immovable_object=True,lost_duel=None)


def test_no_score_contamination():
    r=resolve(has_immovable_object=True,lost_duel=True)
    assert r.dashboard_score is None and r.scenario_score is None
