"""DEV-078-PITS-B: Surprise Attack conditional mechanics acceptance.

Author: Edward Turns (Project Lead)
"""
from dataclasses import replace
import pytest
from pits_surprise_attack import SurpriseAttackContext, resolve_surprise_attack


def context(**kwargs):
    base = SurpriseAttackContext(
        army_list_id='DG_PITS', active_army_rule_ids=('DG_SURPRISE_ATTACK',),
        azog_alive=True, azog_on_battlefield=True, already_used=False,
        declare_surprise_attack=True,
    )
    return replace(base, **kwargs)


def test_normal_activation_wins_priority_and_forbids_enemy_heroic_moves():
    r = resolve_surprise_attack(context())
    assert (r.declared, r.used_after_phase, r.priority_winner,
            r.pits_must_take_priority, r.opposing_heroic_moves_prohibited) == (
                True, True, 'pits', True, True)


def test_rule_usage_is_consumed():
    with pytest.raises(ValueError, match='already been used'):
        resolve_surprise_attack(context(already_used=True))


def test_dead_azog_cannot_activate():
    with pytest.raises(ValueError, match='alive'):
        resolve_surprise_attack(context(azog_alive=False))


def test_azog_off_battlefield_cannot_activate():
    with pytest.raises(ValueError, match='battlefield'):
        resolve_surprise_attack(context(azog_on_battlefield=False))


def test_rule_not_registered_cannot_activate():
    with pytest.raises(ValueError, match='not active'):
        resolve_surprise_attack(context(active_army_rule_ids=()))


def test_wrong_army_cannot_activate():
    with pytest.raises(ValueError, match='not active'):
        resolve_surprise_attack(context(army_list_id='DG_ROTN'))


def test_no_declaration_has_no_effect():
    r = resolve_surprise_attack(context(declare_surprise_attack=False))
    assert not r.declared and not r.used_after_phase
    assert r.priority_winner is None and not r.opposing_heroic_moves_prohibited


def test_no_declaration_preserves_prior_usage():
    r = resolve_surprise_attack(context(declare_surprise_attack=False, already_used=True))
    assert r.used_after_phase and not r.declared


def test_both_declare_waits_for_rolloff_and_burns_usage():
    r = resolve_surprise_attack(context(opponent_declares_equivalent_priority_rule=True))
    assert r.used_after_phase and r.simultaneous_resolution_required
    assert r.priority_winner is None and not r.pits_must_take_priority
    assert r.opposing_heroic_moves_prohibited


def test_simultaneous_pits_wins_rolloff():
    r = resolve_surprise_attack(context(opponent_declares_equivalent_priority_rule=True,
                                         simultaneous_roll_off_winner='pits'))
    assert r.priority_winner == 'pits' and r.pits_must_take_priority
    assert not r.simultaneous_resolution_required


def test_simultaneous_opponent_wins_rolloff_still_burns_rule():
    r = resolve_surprise_attack(context(opponent_declares_equivalent_priority_rule=True,
                                         simultaneous_roll_off_winner='opponent'))
    assert r.priority_winner == 'opponent' and r.used_after_phase
    assert not r.pits_must_take_priority
    assert r.opposing_heroic_moves_prohibited


def test_rolloff_result_without_competing_ability_rejected():
    with pytest.raises(ValueError, match='simultaneous'):
        resolve_surprise_attack(context(simultaneous_roll_off_winner='pits'))


def test_invalid_rolloff_winner_rejected():
    with pytest.raises(ValueError, match='roll_off_winner'):
        resolve_surprise_attack(context(opponent_declares_equivalent_priority_rule=True,
                                         simultaneous_roll_off_winner='tie'))


def test_cannot_supply_nonboolean_context():
    with pytest.raises(TypeError, match='azog_alive'):
        resolve_surprise_attack(context(azog_alive=1))


def test_no_scores_are_generated():
    r = resolve_surprise_attack(context())
    assert r.dashboard_score is None and r.scenario_score is None
