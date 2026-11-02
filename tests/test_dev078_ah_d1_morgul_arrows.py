"""DEV-078-AH-D1 standalone Morgul Arrows acceptance.
Author: Edward Turns (Project Lead)
"""
from fractions import Fraction
import pytest
from morgul_arrows import (
    MorgulArrowsState, register_shooting_wound, resolve_end_phase,
    remove_model, END_PHASE_WOUND_PROBABILITY,
)

BASE = dict(army_list_id="AZOGS_HUNTERS",
            active_army_rule_ids=("DG_MORGUL_ARROWS",),
            attacker_is_friendly=True, target_is_enemy=True,
            attack_is_shooting=True, wound_not_prevented=True)

def hit(state=None, *, turn=1, target_model_id="ENEMY_A", **changes):
    return register_shooting_wound(
        state if state is not None else MorgulArrowsState(),
        turn=turn, target_model_id=target_model_id,
        **{**BASE, **changes},
    )

def test_trigger_unprevented_friendly_shooting_wound():
    assert hit().afflicted == (("ENEMY_A", 1),)

@pytest.mark.parametrize("change", [
    {"attacker_is_friendly": False}, {"target_is_enemy": False},
    {"attack_is_shooting": False}, {"wound_not_prevented": False},
    {"army_list_id": "DG_PITS"}, {"active_army_rule_ids": ()},
])
def test_no_trigger_without_all_conditions(change):
    assert hit(**change).afflicted == ()

def test_multiple_hits_do_not_stack():
    first = hit()
    again = hit(first, target_model_id="ENEMY_A")
    assert again == first

def test_same_turn_end_phase_does_not_roll():
    state, result = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    assert result.rolled_model_ids == ()
    assert result.wounded_model_ids == ()
    assert state.afflicted == (("ENEMY_A", 1),)

def test_following_turn_natural_one_inflicts_wound():
    state, _ = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    state, result = resolve_end_phase(state, turn=2, dice_by_model_id={"ENEMY_A": 1})
    assert result.rolled_model_ids == ("ENEMY_A",)
    assert result.wounded_model_ids == ("ENEMY_A",)
    assert result.wound_probability_per_roll == Fraction(1, 6)
    assert state.afflicted == (("ENEMY_A", 1),)

def test_roll_two_to_six_no_additional_wound():
    state, _ = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    for die in range(2, 7):
        _, result = resolve_end_phase(state, turn=2, dice_by_model_id={"ENEMY_A": die})
        assert result.wounded_model_ids == ()

def test_multiple_targets_one_roll_each():
    state = hit()
    state = hit(state, target_model_id="ENEMY_B")
    state, _ = resolve_end_phase(state, turn=1, dice_by_model_id={})
    state, result = resolve_end_phase(state, turn=2,
                                      dice_by_model_id={"ENEMY_A": 1, "ENEMY_B": 5})
    assert result.rolled_model_ids == ("ENEMY_A", "ENEMY_B")
    assert result.wounded_model_ids == ("ENEMY_A",)

def test_newly_afflicted_model_waits_until_subsequent_turn():
    state, _ = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    state = hit(state, turn=2, target_model_id="ENEMY_B")
    state, result = resolve_end_phase(state, turn=2, dice_by_model_id={"ENEMY_A": 3})
    assert result.rolled_model_ids == ("ENEMY_A",)
    state, result = resolve_end_phase(state, turn=3,
                                      dice_by_model_id={"ENEMY_A": 2, "ENEMY_B": 1})
    assert result.wounded_model_ids == ("ENEMY_B",)

def test_removed_model_no_longer_rolls():
    state = remove_model(hit(), model_id="ENEMY_A")
    _, result = resolve_end_phase(state, turn=2, dice_by_model_id={})
    assert result.rolled_model_ids == ()

def test_remove_unknown_model_is_noop():
    state = hit()
    assert remove_model(state, model_id="UNKNOWN") == state

def test_extra_wound_does_not_end_effect_automatically():
    state, _ = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    state, first = resolve_end_phase(state, turn=2, dice_by_model_id={"ENEMY_A": 1})
    _, second = resolve_end_phase(state, turn=3, dice_by_model_id={"ENEMY_A": 1})
    assert len(first.wounded_model_ids) == len(second.wounded_model_ids) == 1

def test_missing_die_result_rejected():
    with pytest.raises(ValueError, match="Exactly one"):
        resolve_end_phase(hit(), turn=2, dice_by_model_id={})

def test_extra_die_result_rejected():
    with pytest.raises(ValueError, match="Exactly one"):
        resolve_end_phase(hit(), turn=1, dice_by_model_id={"ENEMY_A": 2})

def test_cannot_resolve_same_end_phase_twice():
    state, _ = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    with pytest.raises(ValueError):
        resolve_end_phase(state, turn=1, dice_by_model_id={})

@pytest.mark.parametrize("bad", [0, 7, 1.0, True, None])
def test_invalid_die_result_rejected(bad):
    with pytest.raises(ValueError):
        resolve_end_phase(hit(), turn=2, dice_by_model_id={"ENEMY_A": bad})

def test_bad_registration_time_rejected():
    state, _ = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    with pytest.raises(ValueError):
        hit(state, turn=1, target_model_id="ENEMY_B")

def test_probability_and_scores_are_diagnostic_only():
    assert END_PHASE_WOUND_PROBABILITY == Fraction(1, 6)
    assert MorgulArrowsState().dashboard_score is None
    _, evidence = resolve_end_phase(hit(), turn=1, dice_by_model_id={})
    assert evidence.scenario_score is None
